import os
import uuid
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from urllib.parse import urlparse
import tempfile

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

# Function to upload a single video to S3
def upload_single_to_s3(folder_path, filename):
    try:
        video_id = f"{str(uuid.uuid4())[:8]}_{filename}"
        file_path = os.path.join(folder_path, filename)
        
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
        return video_id, url

    except ClientError as e:
        print(f"Error uploading to S3: {str(e)}")
        raise

# Function to upload bunch of videos to S3 
def upload_to_s3(folder_path):
    video_ids_and_urls = []
    video_files = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
    
    for filename in video_files:
        try:
            video_id = f"{str(uuid.uuid4())[:8]}_{filename}"
            
            file_path = os.path.join(folder_path, filename)
            
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
            video_ids_and_urls.append((video_id, url))

        except ClientError as e:
            print(f"Error uploading to S3: {str(e)}")
            raise
        
    return video_ids_and_urls

def download_from_s3(s3_url):
    """
    Download a video from S3 given its URL and return the temporary file path.
    
    Args:
        s3_url (str): The S3 URL of the video file
        
    Returns:
        str: Path to the temporary file containing the downloaded video
        
    Raises:
        ClientError: If there's an error downloading from S3
        ValueError: If the URL format is invalid
    """
    try:
        # Parse the S3 URL to extract the key
        parsed_url = urlparse(s3_url)
        
        # Extract the key from the URL path (remove leading slash)
        s3_key = parsed_url.path.lstrip('/')
        
        # Validate that this is likely an S3 URL for our bucket
        if AWS_BUCKET_NAME not in parsed_url.netloc:
            raise ValueError(f"URL does not appear to be from the expected S3 bucket: {AWS_BUCKET_NAME}")
        
        # Get the filename from the S3 key
        filename = os.path.basename(s3_key)
        
        # Create a temporary file with the same extension as the original
        file_extension = os.path.splitext(filename)[1] or '.mp4'
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=file_extension,
            prefix='s3_video_'
        )
        temp_file_path = temp_file.name
        temp_file.close()
        
        # Download the file from S3
        print(f"Downloading from S3: {s3_key}")
        s3_client.download_file(
            AWS_BUCKET_NAME,
            s3_key,
            temp_file_path
        )
        
        print(f"Downloaded to temporary file: {temp_file_path}")
        return temp_file_path
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchKey':
            print(f"Error: File not found in S3: {s3_key}")
        else:
            print(f"Error downloading from S3: {str(e)}")
        raise
    except Exception as e:
        # Clean up the temp file if it was created but download failed
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        print(f"Error: {str(e)}")
        raise

def cleanup_temp_file(temp_file_path):
    """
    Helper function to clean up temporary files.
    
    Args:
        temp_file_path (str): Path to the temporary file to delete
    """
    try:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            print(f"Cleaned up temporary file: {temp_file_path}")
    except Exception as e:
        print(f"Warning: Could not clean up temporary file {temp_file_path}: {str(e)}")

def list_s3_urls(prefix="videos-embed/", max_files=20):
    """
    List files in the S3 bucket with the given prefix.
    
    Args:
        prefix (str): S3 key prefix to filter files
        max_files (int): Maximum number of files to return
        
    Returns:
        list: List of dictionaries with file information
    """
    try:
        response = s3_client.list_objects_v2(
            Bucket=AWS_BUCKET_NAME,
            Prefix=prefix,
            MaxKeys=max_files
        )
        
        if 'Contents' not in response:
            print(f"No files found with prefix: {prefix}")
            return []
        
        files = []
        s3_urls = []
        for obj in response['Contents']:
            file_info = {
                'key': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified'],
                'url': f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{obj['Key']}"
            }
            files.append(file_info)
        
        print(f"Found {len(files)} files:")
        for file_info in files:
            print(f"  - {file_info['key']} ({file_info['size']} bytes)")
            print(f"    URL: {file_info['url']}")
            s3_urls.append(file_info['url'])
        
        return s3_urls
        
    except ClientError as e:
        print(f"Error listing S3 files: {str(e)}")
        raise
    
def retrieve_single_s3_url_by_video_id(video_id, max_files=1):
    try:
        video_filename = video_id.split("_", 1)[1]
        prefix = f"videos-embed/{video_filename}"
        response = s3_client.list_objects_v2(
            Bucket=AWS_BUCKET_NAME,
            Prefix=prefix,
            MaxKeys=max_files
        )
        
        if 'Contents' not in response:
            print(f"No files found with prefix: {prefix}")
            return []
        
        files = []
        s3_urls = []
        for obj in response['Contents']:
            file_info = {
                'key': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified'],
                'url': f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{obj['Key']}"
            }
            files.append(file_info)
        
        print(f"Found {len(files)} files:")
        for file_info in files:
            print(f"  - {file_info['key']} ({file_info['size']} bytes)")
            print(f"    URL: {file_info['url']}")
            s3_urls.append(file_info['url'])
        
        return s3_urls[0] if s3_urls else None
        
    except ClientError as e:
        print(f"Error listing S3 files: {str(e)}")
        raise