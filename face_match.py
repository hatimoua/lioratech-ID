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

if __name__ == "__main__":
    result = compare_faces("id.jpg", "selfie.jpg")
    print(result)
