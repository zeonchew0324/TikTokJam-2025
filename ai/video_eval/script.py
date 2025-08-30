import os
import json
import time
import boto3
import requests
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
from google import genai
from google.genai import types
from ai.tech_stack.aws import download_from_s3, cleanup_temp_file, list_s3_files
from prompt import PROMPT

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

client = genai.Client(api_key=GEMINI_API_KEY)

    
def wait_for_file_active(uploaded_file, max_wait_time=300, check_interval=5):
    """
    Wait for the uploaded file to become ACTIVE in Gemini.
    
    Args:
        uploaded_file: The uploaded file object from Gemini
        max_wait_time (int): Maximum time to wait in seconds (default: 5 minutes)
        check_interval (int): Time between status checks in seconds
        
    Returns:
        bool: True if file becomes active, False if timeout
    """
    print(f"Waiting for file {uploaded_file.name} to become ACTIVE...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            # Get current file status
            file_info = client.files.get(name=uploaded_file.name)
            status = file_info.state.name
            print(f"File status: {status}")
            
            if status == 'ACTIVE':
                print("File is now ACTIVE and ready for analysis!")
                return True
            elif status == 'FAILED':
                raise Exception(f"File processing failed: {file_info.error}")
            
            # Wait before checking again
            time.sleep(check_interval)
            
        except Exception as e:
            print(f"Error checking file status: {str(e)}")
            raise
    
    print(f"Timeout: File did not become ACTIVE within {max_wait_time} seconds")
    return False

def score_video_with_gemini(s3_video_url, prompt="Please summarize the video in 3 sentences.", max_wait_time=300, retries=3, delay=2):
    """
    Download video from S3, analyze it with Gemini, and return the response.
    Retry generate_content if JSON parsing fails.
    """
    temp_file_path = None
    uploaded_file = None

    try:
        # Step 1: Download video from S3
        print(f"Starting download from S3: {s3_video_url}")
        temp_file_path = download_from_s3(s3_video_url)

        # Step 2: Upload to Gemini
        print("Uploading video to Gemini for analysis...")
        uploaded_file = client.files.upload(file=temp_file_path)
        print(f"Uploaded to Gemini with URI: {uploaded_file.uri}")

        # Step 3: Wait for file to become ACTIVE
        if not wait_for_file_active(uploaded_file, max_wait_time):
            raise Exception("File did not become ACTIVE within the specified timeout")

        generation_config = {}
        if SCHEMA:
            generation_config['response_schema'] = SCHEMA
            generation_config['response_mime_type'] = 'application/json'

        # Step 4: Generate content with retries
        for attempt in range(1, retries + 1):
            print(f"Generating content with Gemini (Attempt {attempt})...")
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[uploaded_file, prompt],
                config=types.GenerateContentConfig(**generation_config) if generation_config else None
            )
            
            response_text = response.text
            
            try:
                evaluation_data = json.loads(response_text)
                
                # Compute total and normalized scores
                total_score = sum(int(evaluation_data[key]['score']) for key in evaluation_data)
                normalized_score = total_score / 25.0
                evaluation_data['total_score'] = total_score
                evaluation_data['normalized_score'] = normalized_score
                
                print("Analysis complete!")
                return evaluation_data  # success, break out of retry loop
            
            except json.JSONDecodeError as e:
                print(f"[Attempt {attempt}] JSON decode failed: {e}")
                if attempt < retries:
                    print(f"Retrying in {delay * attempt} seconds...")
                    time.sleep(delay * attempt)
                else:
                    print("All retries failed. Returning raw response.")
                    return {"error": "JSON decoding failed", "raw_response": response_text}

    except Exception as e:
        print(f"Error in score_video_with_gemini: {str(e)}")
        raise

    finally:
        if temp_file_path:
            cleanup_temp_file(temp_file_path)
        if uploaded_file:
            try:
                client.files.delete(name=uploaded_file.name)
                print(f"Deleted file from Gemini: {uploaded_file.name}")
            except Exception as e:
                print(f"Warning: Could not delete Gemini file: {str(e)}")


SCHEMA = {
  "type": "object",
  "properties": {
    "artistic_creative_merit": {
      "type": "object",
      "properties": {
        "score": {
          "type": "string",
          "enum": ['1', '2', '3', '4', '5'],
          "description": "A score from 1 to 5 based on the originality and aesthetic appeal of the content."
        },
        "justification": {
          "type": "string",
          "description": "A brief explanation for the assigned score."
        }
      },
      "required": [
        "score",
        "justification"
      ]
    },
    "technical_execution": {
      "type": "object",
      "properties": {
        "score": {
          "type": "string",
          "enum": ['1', '2', '3', '4', '5'],
          "description": "A score from 1 to 5 for the technical quality, including video, audio, and editing."
        },
        "justification": {
          "type": "string",
          "description": "A brief explanation for the assigned score."
        }
      },
      "required": [
        "score",
        "justification"
      ]
    },
    "clarity_cohesion": {
      "type": "object",
      "properties": {
        "score": {
          "type": "string",
          "enum": ['1', '2', '3', '4', '5'],
          "description": "A score from 1 to 5 for how clear and well-structured the content's message is."
        },
        "justification": {
          "type": "string",
          "description": "A brief explanation for the assigned score."
        }
      },
      "required": [
        "score",
        "justification"
      ]
    },
    "value_purpose": {
      "type": "object",
      "properties": {
        "score": {
          "type": "string",
          "enum": ['1', '2', '3', '4', '5'],
          "description": "A score from 1 to 5 for the value the content provides to the viewer."
        },
        "justification": {
          "type": "string",
          "description": "A brief explanation for the assigned score."
        }
      },
      "required": [
        "score",
        "justification"
      ]
    },
    "platform_synergy": {
      "type": "object",
      "properties": {
        "score": {
          "type": "string",
          "enum": ['1', '2', '3', '4', '5'],
          "description": "A score from 1 to 5 for how well the content uses the platform's unique features."
        },
        "justification": {
          "type": "string",
          "description": "A brief explanation for the assigned score."
        }
      },
      "required": [
        "score",
        "justification"
      ]
    }
  },
  "required": [
    "artistic_creative_merit",
    "technical_execution",
    "clarity_cohesion",
    "value_purpose",
    "platform_synergy"
  ]
}

def score_video_normalized(s3_video_url, prompt=PROMPT):
    """
    Wrapper function to score video and return normalized score.
    
    Args:
        s3_video_url (str): S3 URL of the video to analyze
        prompt (str): Custom prompt for Gemini analysis
        
    Returns:
        float: Normalized score between 0 and 1
    """
    evaluation_data = score_video_with_gemini(s3_video_url, prompt)
    
    if 'normalized_score' in evaluation_data:
        return evaluation_data['normalized_score']
    else:
        raise Exception("Failed to obtain normalized score from evaluation data")

# Example usage:
if __name__ == "__main__":
    try:
        s3_url = "https://tiktok-video-embeddings.s3.ap-southeast-1.amazonaws.com/videos-embed/tiktok_6751325446933056770_video.mp4"
        print(f"\nTesting with: {s3_url}")
        
        print("Scoring video...")
        result = score_video_normalized(s3_url, PROMPT)
        print(result)

    except Exception as e:
        print(f"Failed to analyze video: {str(e)}")