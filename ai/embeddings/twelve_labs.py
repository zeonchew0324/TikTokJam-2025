import os
import json
from typing import List
from twelvelabs import TwelveLabs
from twelvelabs.types import VideoSegment
from twelvelabs.embed import TasksStatusResponse
from twelvelabs.indexes import IndexesCreateRequestModelsItem
from twelvelabs.tasks import TasksRetrieveResponse
import time
from dotenv import load_dotenv

load_dotenv()

# Twelve Labs Configuration
INDEX_NAME = "centroid-video-embeddings-index"

# Initialize Twelve Labs client
twelvelabs_client = TwelveLabs(api_key=os.getenv("TL_API_KEY"))

def get_or_create_index(index_name="centroid-video-embeddings-index"):
    # 1. Check if index already exists
    existing_indexes = twelvelabs_client.indexes.list()
    for idx in existing_indexes:   # iterate directly, no `.data`
        if idx.index_name == index_name:
            print(f"Using existing index: id={idx.id}")
            return idx

    # 2. Create new index if not found
    index = twelvelabs_client.indexes.create(
        index_name=index_name,
        models=[
            IndexesCreateRequestModelsItem(
                model_name="pegasus1.2", model_options=["visual", "audio"]
            )
        ]
    )
    print(f"Created new index: id={index.id}")
    return index

index = get_or_create_index(INDEX_NAME)

# Function to fetch video embeddings 
def create_video_embedding(video_url, max_retries=3, retry_delay=5):
    if not twelvelabs_client:
        raise ValueError("Twelve Labs API key not configured")

    retries = 0
    while retries < max_retries:
        try:
            print(f"Creating whole video embedding for {video_url}... (Attempt {retries+1}/{max_retries})")

            task = twelvelabs_client.embed.tasks.create(
                model_name="Marengo-retrieval-2.7",
                video_url=video_url
            )
            print(f"Created video embedding task: id={task.id}")

            def on_task_update(task: TasksStatusResponse):
                print(f"  Status={task.status}")

            status = twelvelabs_client.embed.tasks.wait_for_done(sleep_interval=5, task_id=task.id, callback=on_task_update)
            print(f"Embedding done: {status.status}")

            task_result = twelvelabs_client.embed.tasks.retrieve(
                task_id=task.id,
                embedding_option=["visual-text", "audio"]
            )

            def print_segments(segments: List[VideoSegment], max_elements: int = 5):
                for segment in segments:
                    print(f"  embedding_scope={segment.embedding_scope} embedding_option={segment.embedding_option} start_offset_sec={segment.start_offset_sec} end_offset_sec={segment.end_offset_sec}")
                    first_few = segment.float_[:max_elements]
                    print(
                        f"  embeddings: [{', '.join(str(x) for x in first_few)}...] (total: {len(segment.float_)} values)"
                    )

            if task_result.status != 'ready':
                raise ValueError(f"Task failed with status: {task_result.status}")

            if task_result.video_embedding is not None and task_result.video_embedding.segments is not None:
                print_segments(task_result.video_embedding.segments)

            return task_result

        except Exception as e:
            print(f"Error creating embedding (attempt {retries+1}): {str(e)}")
            retries += 1
            if retries < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                print("Max retries reached, giving up.")
                raise

# Function to categorize video using Twelve Labs
def categorize(video_url):
    # 1. Upload a video
    task = twelvelabs_client.tasks.create(
        index_id=index.id, video_url=video_url)
    print(f"Created task: id={task.id}")

    # 2. Monitor the indexing process
    def on_task_update(task: TasksRetrieveResponse):
        print(f"  Status={task.status}")

    task = twelvelabs_client.tasks.wait_for_done(
        sleep_interval=5, task_id=task.id, callback=on_task_update)
    if task.status != "ready":
        raise RuntimeError(f"Indexing failed with status {task.status}")
    print(
        f"Upload complete. The unique identifier of your video is {task.video_id}.")

    # 3. Perform open-ended analysis
    response = twelvelabs_client.analyze(
        video_id=task.video_id,
        prompt="Classify this video based on YouTube categories. Output as JSON format with 'category' field.",
        temperature=0
    )

    response = response.data
    
    parsed_json = json.loads(response)
    
    category = parsed_json.get('category', 'Unknown')
    
    return category
            
print(categorize("https://tiktok-video-embeddings.s3.ap-southeast-1.amazonaws.com/videos-embed/e4650511_Car2.mp4"))