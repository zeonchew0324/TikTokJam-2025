import ast
import os

def parse_video_url_map(file_path):
    """
    Parses a text file containing video file and URL pairs.

    Each line in the file is expected to be a string representation of a
    Python list, e.g., '["filename.mp4", "https://example.com/url.mp4"]'.
    This function reads the file and converts the data into a list of
    tuples.

    Args:
        file_path (str): The path to the input text file.

    Returns:
        list: A list of tuples, where each tuple contains two strings
              (video filename, video URL).
    """
    parsed_data = []
    
    # Check if the file exists to prevent errors
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found.")
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Remove leading/trailing whitespace and the outer quotes
                cleaned_line = line.strip().strip('"')
                if not cleaned_line:
                    continue  # Skip empty lines

                try:
                    # Safely evaluate the string as a Python literal
                    # ast.literal_eval is safer than eval() for parsing literals
                    item_list = ast.literal_eval(cleaned_line)
                    
                    # Ensure the parsed item is a list with two elements
                    if isinstance(item_list, list) and len(item_list) == 2:
                        parsed_data.append(tuple(item_list))
                    else:
                        print(f"Warning: Skipping malformed line: {line.strip()}")
                except (ValueError, SyntaxError) as e:
                    print(f"Error parsing line: {line.strip()} - {e}")
                    
        return parsed_data

    except IOError as e:
        print(f"Error reading the file: {e}")
        return []

    return parsed_data