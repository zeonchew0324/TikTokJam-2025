import os
import json
import random
from datetime import datetime
from ai.tech_stack.aws import upload_single_to_s3 

VIDEO_CONTENT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai', 'video_content')
SQL_OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'output.sql')
TABLE_NAME = 'video_output'

def get_random_watch_time(duration):
    if duration:
        return random.randint(int(duration * 0.5), int(duration))
    return random.randint(5, 60)

def get_random_views():
    return random.randint(100, 10000)

def get_json_value(data, key, default=None):
    return data.get(key, default)

def generate_unique_numbers(n=1000, start=1, end=1000):
    """
    Generate n unique random numbers from start to end (inclusive) without replacement.
    """
    if n > (end - start + 1):
        raise ValueError("n is larger than the range of numbers")
    return random.sample(range(start, end + 1), n)


def main():
    sql_lines = []

    for category in os.listdir(VIDEO_CONTENT_DIR):
        category_path = os.path.join(VIDEO_CONTENT_DIR, category)
        print(f"Processing category: {category}")

        if not os.path.isdir(category_path):
            continue

        json_dir = os.path.join(category_path, 'json_files')
        print(f"json_dir: {json_dir}")
        video_dir = os.path.join(category_path, 'videos')
        print(f"video_dir: {video_dir}")

        if not os.path.isdir(json_dir):
            print(f"[DEBUG] No json_files directory in: {category_path}")
            continue

        for json_file in os.listdir(json_dir):
            if not json_file.endswith('.json'):
                continue

            json_path = os.path.join(json_dir, json_file)
            base_name = os.path.splitext(json_file)[0]
            if base_name.endswith("_metadata"):
                base_name = base_name[:-9] 
            video_filename = base_name + "_video.mp4"
            print(f"video_filename: {video_filename}")

            # Skip if JSON file does not exist
            if not os.path.exists(json_path):
                print(f"[DEBUG] JSON file not found, skipping: {json_path}")
                continue

            # Try reading the JSON
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"[DEBUG] Error reading JSON {json_path}, skipping. Error: {e}")
                continue

            # Corresponding video file (assume mp4, same basename)
            video_id, video_url = upload_single_to_s3(video_dir, video_filename)
            caption = get_json_value(data.get('video_metadata', {}), 'description', '')
            creator_id = generate_unique_numbers(1)[0]  # single unique number
            duration = get_json_value(data.get('file_metadata', {}), 'duration', 0)
            watch_time = get_json_value(data.get('video_metadata', {}), 'watch_time', None) or get_random_watch_time(duration)
            pastmonthsviewcount = get_random_views()
            totalviewcount = get_json_value(data.get('video_metadata', {}), 'playcount', get_random_views())
            if pastmonthsviewcount < totalviewcount:
                # If past month's views are less than total views, adjust accordingly
                pastmonthsviewcount = int(totalviewcount * 0.75)
            likecount = get_json_value(data.get('video_metadata', {}), 'diggcount', 0)
            commentcount = get_json_value(data.get('video_metadata', {}), 'commentcount', 0)
            createdat = get_json_value(data.get('video_metadata', {}), 'time_created', None)
            if createdat:
                try:
                    createdat = datetime.fromtimestamp(int(createdat)).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    createdat = str(createdat)
            else:
                createdat = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            def esc(val):
                if isinstance(val, str):
                    return val.replace("'", "''")
                return val

            sql = f"INSERT INTO {TABLE_NAME} (video_id, caption, creator_id, duration, watch_time, video_url, past_months_view_count, total_view_count, like_count, comment_count, created_at) VALUES \
('{esc(video_id)}', '{esc(caption)}', '{esc(creator_id)}', {duration}, {watch_time}, '{esc(video_url)}', {pastmonthsviewcount}, {totalviewcount}, {likecount}, {commentcount}, '{esc(createdat)}');"

            sql_lines.append(sql)
            print(f"[DEBUG] Added SQL for {json_file}")

    # Write all SQL lines to output file
    with open(SQL_OUTPUT_FILE, 'w') as f:
        f.write("\n".join(sql_lines))

    print(f"SQL output written to {SQL_OUTPUT_FILE}")

if __name__ == "__main__":
    main()
