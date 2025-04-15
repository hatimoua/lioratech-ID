import os
import re
import json
from PIL import Image
import boto3
from dotenv import load_dotenv
from s3_utils import upload_image_to_s3

load_dotenv()

rekognition = boto3.client(
    'rekognition',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

def extract_id_fields(image_path):
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    response = rekognition.detect_text(Image={"Bytes": image_bytes})
    text_detections = response.get("TextDetections", [])
    lines = [d["DetectedText"] for d in text_detections if d["Type"] == "LINE"]
    text = " ".join(lines)

    dob_match = re.search(r"\d{4}-\d{2}-\d{2}", text)
    id_match = re.search(r"T\d{4}-\d{6}-\d{2}", text)
    name_match = re.findall(r"\b[A-Z]{3,}\b", text)

    return {
        "Name": f"{name_match[0]} {name_match[1]}" if len(name_match) > 1 else "Not found",
        "Date of Birth": dob_match.group(0) if dob_match else "Not found",
        "ID Number": id_match.group(0) if id_match else "Not found",
        "Raw OCR Text": text
    }

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

def verify_id_and_face(id_image, selfie_image):
    fields = extract_id_fields(id_image)
    face_result = compare_faces(id_image, selfie_image)

    verdict = "PASS" if face_result["score"] >= 90 else "REVIEW" if face_result["score"] >= 80 else "FAIL"

    # Upload to S3 and get URLs
    with open(id_image, "rb") as f:
        id_url = upload_image_to_s3(f.read())
    with open(selfie_image, "rb") as f:
        selfie_url = upload_image_to_s3(f.read())

    result = {
        **fields,
        "Face Match Score": round(face_result["score"], 2),
        "Verdict": verdict,
        "ID Image URL": id_url,
        "Selfie Image URL": selfie_url
    }

    with open("verification_result.json", "w") as f:
        json.dump(result, f, indent=4)

    return result

if __name__ == "__main__":
    result = verify_id_and_face("id.jpg", "selfie.jpg")
    for k, v in result.items():
        print(f"{k}: {v}")
    print("✅ Saved JSON to verification_result.json")

def compare_faces(source_image_path, target_image_path, threshold=90):
    try:
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
    
    except Exception as e:
        return {"match": False, "score": 0, "error": str(e)}
