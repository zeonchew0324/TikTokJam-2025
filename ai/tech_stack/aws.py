import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

# AWS Configuration
AWS_BUCKET_NAME = "tiktok-video-embeddings"
AWS_REGION = "ap-southeast-1"

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    region_name=AWS_REGION
)

# Function to upload videos to S3
def upload_to_s3(file_path, filename):
    try:
        # Upload the file
        s3_client.upload_file(
            file_path,
            AWS_BUCKET_NAME,
            f"videos-embed/{filename}",
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': 'video/mp4'
            }
        )

        # Generate the public URL
        url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/videos-embed/{filename}"
        print(f"Uploaded to S3: {url}")
        return url

    except ClientError as e:
        print(f"Error uploading to S3: {str(e)}")
        raise