import sys
import asyncio
from pathlib import Path

from helper_funtions import (
    DEFAULT_MODEL,
    cancel_all_jobs,
    check_status,
    parse_results,
    process_jsonl_parts,
)
from jsonl_convertor import JSONLConverter
from logger import Tee


# ---- stdout tee logging -------------
log_file = Path("temp/logs/batch_llm_filter.log")
log_file.parent.mkdir(parents=True, exist_ok=True)
sys.stdout = Tee(sys.stdout, log_file.open("w", encoding="utf-8"))
# -------------------------------------


def main(
    filtered_patches_path: str,
    batch_jsonl_path: str,
    response_jsonl_path: str,
    llm_filtered_path: str,
    jsonl_filename: str,
    results_filename: str,
):
    entry = (
        "1: Generate JSONL file. \n"
        "2: Start batch processing (requires existing JSONL file).\n"
        "3: Check status of batch job.\n"
        "4: Parse results and save filtered notes (requires existing results.jsonl file).\n"
        "5: Cancel all active batch jobs.\n"
        "Input: "
    )
    u_entry = input(entry)

    while u_entry not in ["1", "2", "3", "4", "5"]:
        print("Invalid entry. Please enter 1, 2, 3, 4, or 5.")
        u_entry = input(entry)

    if u_entry == "1":
        converter = JSONLConverter(filtered_patches_path, batch_jsonl_path, jsonl_filename)
        converter.generate_jsonl_parts()

        u_input = input("JSONL generation completed successfully. Do you want to proceed with the batch job? (y/n): ")
        if u_input.lower() == "y":
            print("Starting batch job.")
            asyncio.run(process_jsonl_parts(batch_jsonl_path, response_jsonl_path, results_filename, model=DEFAULT_MODEL))
            u_input = input("Batch job completed. Do you want to proceed with results parsing? (y/n): ")
            if u_input.lower() == "y":
                print("Starting results parsing.")
                parse_results(response_jsonl_path, filtered_patches_path, llm_filtered_path, results_filename)
            else:
                print("Results parsing skipped. You can run it later using option 4.")
        else:
            print("Batch job skipped. You can run them later using options 2")

    if u_entry == "2":
        asyncio.run(process_jsonl_parts(batch_jsonl_path, response_jsonl_path, results_filename, model=DEFAULT_MODEL))
        u_input = input("Batch job completed. Do you want to proceed with results parsing? (y/n): ")
        if u_input.lower() == "y":
            print("Starting results parsing.")
            parse_results(response_jsonl_path, filtered_patches_path, llm_filtered_path, results_filename)
        else:
            print("Results parsing skipped. You can run it later using option 4.")

    if u_entry == "3":
        all_done = asyncio.run(check_status(batch_jsonl_path, response_jsonl_path, results_filename, model=DEFAULT_MODEL))
        if all_done:
            u_input = input("All jobs completed. Do you want to proceed with results parsing? (y/n): ")
            if u_input.lower() == "y":
                print("Starting results parsing.")
                parse_results(response_jsonl_path, filtered_patches_path, llm_filtered_path, results_filename)
            else:
                print("Results parsing skipped. You can run it later using option 4.")

    if u_entry == "4":
        parse_results(response_jsonl_path, filtered_patches_path, llm_filtered_path, results_filename)

    if u_entry == "5":
        asyncio.run(cancel_all_jobs(batch_jsonl_path, response_jsonl_path, results_filename, model=DEFAULT_MODEL))
        print("Run option 2 to re-submit cancelled parts.")


if __name__ == "__main__":
    filtered_patches_path = "patches/filtered_patches"
    llm_filtered_path = "patches/llm_filtered_patches"

    batch_jsonl_path = "scripts/llm_filtering/batch_process/jsonl"
    response_jsonl_path = "scripts/llm_filtering/batch_process/jsonl/result_parts"
    jsonl_filename = "batch.jsonl"
    results_filename = "results.jsonl"

    main(
        filtered_patches_path=filtered_patches_path,
        batch_jsonl_path=batch_jsonl_path,
        response_jsonl_path=response_jsonl_path,
        llm_filtered_path=llm_filtered_path,
        jsonl_filename=jsonl_filename,
        results_filename=results_filename,
    )
