import asyncio
import json
from pathlib import Path

from config import DEFAULT_MODEL, MAX_CONCURRENT, JOB_ID_PATH
from job_processor import JobProcessor
from results_parser import ResultParser


async def process_jsonl_parts(
    batch_jsonl_path: str,
    response_jsonl_path: str,
    results_filename: str,
    model: str = DEFAULT_MODEL,
):
    parts_path = Path(batch_jsonl_path) / "batch_parts"
    pending = list(sorted(parts_path.glob("*.jsonl")))

    if not pending:
        print("No JSONL parts found in batch_parts/")
        return

    existing_jobs = {}
    if JOB_ID_PATH.exists():
        content = JOB_ID_PATH.read_text().strip()
        if content:
            existing_jobs = json.loads(content)

    print(f"Found {len(pending)} parts.")

    polling_tasks = {}

    async def submit_one(file):
        processor = JobProcessor(parts_path, response_jsonl_path, file.name, results_filename, model=model)
        await processor.upload_jsonl()
        await processor.create_job()
        return file, processor

    async def resume_part(file, job_id):
        processor = JobProcessor(parts_path, response_jsonl_path, file.name, results_filename, model=model)
        await processor.poll_and_download(job_id=job_id)
        return file

    async def poll_part(processor, file):
        await processor.poll_and_download(job_id=processor.job.name)
        return file

    async def wait_for_one():
        done, _ = await asyncio.wait(polling_tasks.keys(), return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            file = polling_tasks.pop(task)
            try:
                task.result()
                print(f"[{file.name}] DONE")
            except Exception as e:
                print(f"[{file.name}] FAILED during polling: {e}")

    while pending:
        file = pending.pop(0)

        if file.name in existing_jobs:
            print(f"[{file.name}] Resuming - already has job ID")
            task = asyncio.create_task(resume_part(file, existing_jobs[file.name]))
            polling_tasks[task] = file
            continue

        if len(polling_tasks) >= MAX_CONCURRENT:
            print(f"At capacity ({MAX_CONCURRENT} in-flight). Waiting for one to finish...")
            await wait_for_one()

        try:
            file, processor = await submit_one(file)
            task = asyncio.create_task(poll_part(processor, file))
            polling_tasks[task] = file
            print(f"[{file.name}] Submitted - polling in background")
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print(f"[{file.name}] Rate limited - waiting for one job to finish")
                pending.insert(0, file)
                if polling_tasks:
                    await wait_for_one()
                else:
                    print("No running jobs to wait for. Waiting 500s...")
                    await asyncio.sleep(500)
            else:
                print(f"[{file.name}] FAILED: {e}")

    if polling_tasks:
        print(f"All parts submitted. Waiting for {len(polling_tasks)} remaining jobs...")
        done, _ = await asyncio.wait(polling_tasks.keys())
        for task in done:
            file = polling_tasks.pop(task)
            try:
                task.result()
                print(f"[{file.name}] DONE")
            except Exception as e:
                print(f"[{file.name}] FAILED during polling: {e}")

    print("All parts processed.")


async def check_status(
    batch_jsonl_path: str,
    response_jsonl_path: str,
    results_filename: str,
    model: str = DEFAULT_MODEL,
):
    if not JOB_ID_PATH.exists():
        print("No job IDs found. Run batch processing first (option 2).")
        return False

    job_ids = json.loads(JOB_ID_PATH.read_text())
    parts_path = Path(batch_jsonl_path) / "batch_parts"

    print(f"Checking status of {len(job_ids)} jobs...")

    tasks = []
    part_names = []
    for jsonl_name, job_id in job_ids.items():
        processor = JobProcessor(parts_path, response_jsonl_path, jsonl_name, results_filename, model=model)
        tasks.append(asyncio.create_task(processor.poll_and_download(job_id=job_id)))
        part_names.append(jsonl_name)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_done = True
    for i, result in enumerate(results):
        name = part_names[i]
        if isinstance(result, Exception):
            print(f"[{name}] FAILED or STILL RUNNING: {result}")
            all_done = False
        else:
            print(f"[{name}] DONE")

    if all_done:
        return True

    print("Some parts are not done yet. Re-run option 3 later.")
    return False


async def cancel_all_jobs(
    batch_jsonl_path: str,
    response_jsonl_path: str,
    results_filename: str,
    model: str = DEFAULT_MODEL,
):
    if not JOB_ID_PATH.exists():
        print("No job IDs found.")
        return

    job_ids = json.loads(JOB_ID_PATH.read_text())
    parts_path = Path(batch_jsonl_path) / "batch_parts"

    print(f"Cancelling {len(job_ids)} jobs...")

    tasks = []
    part_names = []
    for jsonl_name, job_id in job_ids.items():
        processor = JobProcessor(parts_path, response_jsonl_path, jsonl_name, results_filename, model=model)
        tasks.append(asyncio.create_task(processor.cancel_job(job_id=job_id)))
        part_names.append(jsonl_name)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    cancelled = 0
    for i, result in enumerate(results):
        name = part_names[i]
        if isinstance(result, Exception):
            print(f"[{name}] Cancel error: {result}")
        elif result:
            processor = JobProcessor(parts_path, response_jsonl_path, name, results_filename, model=model)
            processor._remove_job_id()
            cancelled += 1
        else:
            print(f"[{name}] Was already in terminal state")

    print(f"Cancelled {cancelled}/{len(job_ids)} jobs. Upload IDs preserved for re-submission.")


def parse_results(results_jsonl_path: str, notes_path: str, filtered_notes_path: str, filename: str):
    parser = ResultParser(
        results_path=results_jsonl_path,
        notes_path=notes_path,
        filtered_notes_path=filtered_notes_path,
        filename=filename,
    )

    results_path = Path(results_jsonl_path)
    part_files = [f.name for f in sorted(results_path.glob("results_part_*.jsonl"))]
    if part_files:
        parser.merge_results(part_files)

    results_map = parser.parse_results()
    parser.apply_tags(results_map)
