from pathlib import Path
from files_handler import FileHandler

if __name__ == "__main__":
    input_path = Path("patches_sample")  
    output_path = Path("results") 
    handler = FileHandler(input_path, output_path)
    handler.process_is_patch_notes()