import boto3
import os
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

def upload_to_s3(file_path, bucket, key):
    with open(file_path, "rb") as f:
        s3.upload_fileobj(f, bucket, key)
    print(f"✅ Uploaded to s3://{bucket}/{key}")
    return f"https://{bucket}.s3.amazonaws.com/{key}"

def generate_presigned_url(bucket, key, expiration=3600):
    return s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=expiration
    )
