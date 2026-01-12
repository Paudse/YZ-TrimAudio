import shutil
from pathlib import Path

INPUT_DIR = "C:/Users/b9220/Desktop/input_m4a"
OUTPUT_DIR = "C:/Users/b9220/Desktop/output_m4a"

def clean_folder(path):
    path = Path(path)
    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

clean_folder(INPUT_DIR)
clean_folder(OUTPUT_DIR)
