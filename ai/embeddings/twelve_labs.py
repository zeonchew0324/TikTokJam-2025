import os
from typing import List
from twelvelabs import TwelveLabs
from twelvelabs.types import VideoSegment
from twelvelabs.embed import TasksStatusResponse
import time
from dotenv import load_dotenv

load_dotenv()

# Initialize Twelve Labs client
twelvelabs_client = TwelveLabs(api_key=os.getenv("TL_API_KEY"))

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