# Updated version using Rekognition OCR

import os
import re
import json
import pytesseract
from PIL import Image
import boto3
from dotenv import load_dotenv

load_dotenv()

# Set up Rekognition
rekognition = boto3.client(
    'rekognition',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

# Run OCR + extract fields
def extract_id_fields(image_path):
    text = pytesseract.image_to_string(Image.open(image_path), lang='eng')
    text = text.replace("\n", " ").replace("–", "-").replace("—", "-")

    dob_match = re.search(r"Date de naissance.*?(\d{4}-\d{2}-\d{2})", text)
    dob = dob_match.group(1) if dob_match else "Not found"

    id_match = re.search(r"T\d{4}-\d{6}-\d{2}", text)
    id_number = id_match.group(0) if id_match else "Not found"

    name_lines = re.findall(r"\b[A-Z]{3,}\b", text)
    name = f"{name_lines[0]} {name_lines[1]}" if len(name_lines) > 1 else "Not found"

    return {
        "Name": name,
        "Date of Birth": dob,
        "ID Number": id_number,
        "Raw OCR Text": text
    }

# Face comparison
def compare_faces(source_image_path, target_image_path, threshold=90):
    with open(source_image_path, "rb") as src:
        source_bytes = src.read()
    with open(target_image_path, "rb") as tgt:
        target_bytes = tgt.read()

    response = rekognition.compare_faces(
        SourceImage={'Bytes': source_bytes},
        TargetImage={'Bytes': target_bytes},
        SimilarityThreshold=threshold
    )

    if response['FaceMatches']:
        similarity = response['FaceMatches'][0]['Similarity']
        return {"match": True, "score": similarity}
    else:
        return {"match": False, "score": 0}

# Unified verification
def verify_id_and_face(id_image, selfie_image):
    fields = extract_id_fields(id_image)
    face_result = compare_faces(id_image, selfie_image)

    verdict = "PASS" if face_result["score"] >= 90 else "REVIEW" if face_result["score"] >= 80 else "FAIL"

    result = {
        **fields,
        "Face Match Score": round(face_result["score"], 2),
        "Verdict": verdict
    }

    with open("verification_result.json", "w") as f:
        json.dump(result, f, indent=4)

    return result

# Run CLI
if __name__ == "__main__":
    result = verify_id_and_face("id.jpg", "selfie.jpg")
    for k, v in result.items():
        print(f"{k}: {v}")
    print("✅ Saved JSON to verification_result.json")

