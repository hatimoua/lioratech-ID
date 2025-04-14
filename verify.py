import boto3
import os
from dotenv import load_dotenv

load_dotenv()

rekognition = boto3.client(
    'rekognition',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

def load_image_bytes(path):
    with open(path, 'rb') as img:
        return img.read()

def compare_faces(id_img, selfie_img, threshold=90):
    response = rekognition.compare_faces(
        SourceImage={'Bytes': load_image_bytes(id_img)},
        TargetImage={'Bytes': load_image_bytes(selfie_img)},
        SimilarityThreshold=threshold
    )
    return response.get('FaceMatches', [])

def extract_text(id_img):
    response = rekognition.detect_text(
        Image={'Bytes': load_image_bytes(id_img)}
    )
    return [d['DetectedText'] for d in response['TextDetections']]

if __name__ == "__main__":
    id_image = "id.jpg"
    selfie_image = "selfie.jpg"

    print("🔍 Comparing faces...")
    matches = compare_faces(id_image, selfie_image)
    if matches:
        print(f"✅ Match found: {matches[0]['Similarity']:.2f}%")
    else:
        print("❌ No match found.")

    print("\n🧾 Extracted text from ID:")
    for line in extract_text(id_image):
        print("-", line)
