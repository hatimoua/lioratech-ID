import boto3
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

def upload_image_to_s3(image_bytes, file_type="jpg", folder="captures"):
    unique_filename = f"{folder}/{uuid.uuid4()}.{file_type}"
    bucket = "lioratech-id-captures"

    s3.put_object(
        Bucket=bucket,
        Key=unique_filename,
        Body=image_bytes,
        ContentType=f"image/{file_type}",
        ACL="public-read"  # optional — only if you want the URL to be accessible
    )

    return f"https://{bucket}.s3.amazonaws.com/{unique_filename}"
