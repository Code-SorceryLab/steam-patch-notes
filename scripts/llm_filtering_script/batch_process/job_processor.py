import json
import os
import asyncio
from google import genai
from google.genai import types
from pathlib import Path
from dotenv import load_dotenv

from config import JOB_ID_PATH, UPLOAD_ID_PATH
from file_handler import FileHandler

load_dotenv()


class JobProcessor:
    def __init__(
        self,
        input_path: str,
        output_path: str,
        jsonl_name: str,
        filename: str = "results.jsonl",
        model: str = "gemini-2.5-flash-lite",
    ):
        self.handler = FileHandler(input_path, output_path)
        self.filename = filename
        self.jsonl_name = jsonl_name
        self.model = model
        self.part_result_filename = f"results_{Path(jsonl_name).stem}.jsonl"
        self.client = genai.Client(api_key=os.getenv("API_KEY"))
        self.uploaded = None

        print(f"[{self.jsonl_name}] Initialized processor")

        Path(output_path).mkdir(parents=True, exist_ok=True)

    async def upload_jsonl(self):
        # Reuse existing upload if available
        existing = self._load_upload_id()
        if existing:
            print(f"[{self.jsonl_name}] Reusing existing upload: {existing}")
            self.uploaded = type("Upload", (), {"name": existing})()
            return

        self.uploaded = await self.client.aio.files.upload(
            file=str(self.handler.import_jsonl(self.jsonl_name)),
            config=types.UploadFileConfig(
                display_name=f"patchnote-batch-input-{self.jsonl_name}",
                mime_type="jsonl",
            ),
        )
        self._save_upload_id(self.uploaded.name)
        print(f"[{self.jsonl_name}] Uploaded: {self.uploaded.name}")

    async def create_job(self):
        self.job = await self.client.aio.batches.create(
            model=self.model,
            src=self.uploaded.name,
            config=types.CreateBatchJobConfig(
                display_name=f"patchnote-filter-job-{self.jsonl_name}",
            ),
        )

        print(f"[{self.jsonl_name}] Job created: {self.job.name}")
        self._save_job_id(self.job.name)
        return self.job.name

    async def poll_and_download(self, job_id=None):
        if job_id is None:
            job_id = self._load_job_id()

        while True:
            status = await self.client.aio.batches.get(name=job_id)
            state = status.state.name
            print(f"[{self.jsonl_name}] State: {state}")

            if state == "JOB_STATE_SUCCEEDED":
                break
            if state in ["JOB_STATE_FAILED", "JOB_STATE_CANCELLED"]:
                raise RuntimeError(f"[{self.jsonl_name}] Batch failed: {status.error}")

            await asyncio.sleep(10)

        await self._download_results(status)
        return state

    async def _download_results(self, status):
        result_file = status.dest.file_name
        result_bytes = await self.client.aio.files.download(file=result_file)

        self.handler.export_download(result_bytes, self.part_result_filename)
        print(f"[{self.jsonl_name}] Downloaded results to {self.part_result_filename}")

        part_path = self.handler.input_path / self.jsonl_name
        if part_path.exists():
            part_path.unlink()
            print(f"[{self.jsonl_name}] Deleted part file")

        # Remove the upload id once this part finishes successfully
        if UPLOAD_ID_PATH.exists():
            content = UPLOAD_ID_PATH.read_text().strip()
            if content:
                upload_ids = json.loads(content)
                upload_ids.pop(self.jsonl_name, None)
                UPLOAD_ID_PATH.write_text(json.dumps(upload_ids, indent=2))

    async def cancel_job(self, job_id=None):
        if job_id is None:
            job_id = self._load_job_id()

        try:
            status = await self.client.aio.batches.get(name=job_id)
            state = status.state.name

            if state in ("JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED"):
                print(f"[{self.jsonl_name}] Already in terminal state: {state}")
                return False

            await self.client.aio.batches.cancel(name=job_id)
            print(f"[{self.jsonl_name}] Cancelled job: {job_id}")
            return True
        except Exception as e:
            print(f"[{self.jsonl_name}] Error cancelling: {e}")
            return False

    def _remove_job_id(self):
        if JOB_ID_PATH.exists():
            content = JOB_ID_PATH.read_text().strip()
            if content:
                job_ids = json.loads(content)
                job_ids.pop(self.jsonl_name, None)
                JOB_ID_PATH.write_text(json.dumps(job_ids, indent=2))

    async def process(self):
        await self.upload_jsonl()
        job_id = await self.create_job()
        await self.poll_and_download(job_id=job_id)
        return self.part_result_filename

    def _save_job_id(self, job_id):
        job_ids = {}
        if JOB_ID_PATH.exists():
            content = JOB_ID_PATH.read_text().strip()
            if content:
                job_ids = json.loads(content)
        job_ids[self.jsonl_name] = job_id
        JOB_ID_PATH.write_text(json.dumps(job_ids, indent=2))

    def _load_job_id(self):
        job_ids = json.loads(JOB_ID_PATH.read_text())
        return job_ids[self.jsonl_name]

    def _save_upload_id(self, upload_id):
        upload_ids = {}
        if UPLOAD_ID_PATH.exists():
            content = UPLOAD_ID_PATH.read_text().strip()
            if content:
                upload_ids = json.loads(content)
        upload_ids[self.jsonl_name] = upload_id
        UPLOAD_ID_PATH.write_text(json.dumps(upload_ids, indent=2))

    def _load_upload_id(self):
        if UPLOAD_ID_PATH.exists():
            content = UPLOAD_ID_PATH.read_text().strip()
            if content:
                upload_ids = json.loads(content)
                return upload_ids.get(self.jsonl_name)
        return None
