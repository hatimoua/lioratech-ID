import pytesseract
from PIL import Image
import re

def extract_id_fields(image_path):
    text = pytesseract.image_to_string(Image.open(image_path), lang='eng')

    # Normalize the text to improve regex hits
    text = text.replace("\n", " ").replace("–", "-").replace("—", "-")

    # DOB: Grab date next to "Date de naissance"
    dob_match = re.search(r"Date de naissance.*?(\d{4}-\d{2}-\d{2})", text)
    dob = dob_match.group(1) if dob_match else "Not found"

    # ID Number: Look for Txxxx-xxxxxx-xx pattern
    id_match = re.search(r"T\d{4}-\d{6}-\d{2}", text)
    id_number = id_match.group(0) if id_match else "Not found"

    # Name: Use known location/structure assumption
    name_lines = re.findall(r"\b[A-Z]{3,}\b", text)
    name = f"{name_lines[0]} {name_lines[1]}" if len(name_lines) > 1 else "Not found"

    return {
        "Name": name,
        "Date of Birth": dob,
        "ID Number": id_number,
        "Raw OCR Text": text
    }

if __name__ == "__main__":
    result = extract_id_fields("id.jpg")
    for k, v in result.items():
        print(f"{k}: {v}")

import json

def save_to_json(result_dict, filename="output.json"):
    with open(filename, "w") as f:
        json.dump(result_dict, f, indent=4)

fields = extract_id_fields("id.jpg")
save_to_json(fields)
print("✅ Saved result to output.json")
