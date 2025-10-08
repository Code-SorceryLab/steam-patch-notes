from pathlib import Path
from files_handler import FileHandler

def main(input_path, output_path):
    input_path = Path(input_path)  
    output_path = Path(output_path) 
    handler = FileHandler(input_path, output_path)
    handler.process_is_patch_notes()

if __name__ == "__main__":
    main()