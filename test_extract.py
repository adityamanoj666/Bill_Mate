from pathlib import Path 
from extractor import extract_receipt

image_bytes=Path("receipt.jpg").read_bytes()
receipt=extract_receipt(image_bytes,"image/jpeg")
print(receipt.model_dump_json(indent=2))