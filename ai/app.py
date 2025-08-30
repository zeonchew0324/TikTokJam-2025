# Import the Flask class from the flask module
from flask import Flask, jsonify, render_template, request
import pandas as pd

from ai.bot_detection.main import aggregate_per_user, bot_probabilities
from ai.categorize_video.main import categorize_video_into_3_categories
from ai.evaluate_video_quality.main import evaluate_video_quality, evaluate_video_quality_batch
from ai.cluster_videos.main import cluster_videos_into_category
from ai.visualize_clustering_algo.main import visualize_clustering_algo

# Create an instance of the Flask class
# __name__ is a special variable that gets the name of the current file
# This helps Flask find resources like templates and static files
app = Flask(__name__)

# Define a route for the homepage
# The @app.route decorator binds a URL to a function
@app.route('/')
def index():
    """
    This function is called when a user navigates to the root URL (/) of the app.
    It returns a simple string that will be displayed in the browser.
    """
    return "Hello, World!"

# Another route with a variable part
# <name> is a dynamic part of the URL
@app.route('/hello/<name>')
def hello_name(name):
    """
    This function takes the dynamic part of the URL (name) as an argument.
    It returns a personalized greeting.
    """
    return f"Hello, {name}!"

# A route that renders an HTML template
# This is useful for building web pages with more structure
# You would need to create a 'templates' folder and an 'about.html' file
@app.route('/about')
def about():
    """
    This function renders an HTML template.
    You can pass data to the template using keyword arguments.
    """
    return render_template('about.html', title='About Us', content='This is the about page.')

# ------------------------------------------
# Real Endpoints and Logic would go below
# ------------------------------------------

@app.route('/admin/run-bot-user-check', methods=['POST'])
def run_bot_user_check_endpoint():
    """
    CHECK IF USERS ARE BOTS
    EXPECTS: JSON payload with 'events': list of event dicts
    """
    # Get JSON data from request
    data = request.get_json()

    if not data or "events" not in data:
        return jsonify({"error": "Missing 'events' in request body"}), 400

    events = data["events"]

    # Convert list of events → DataFrame
    df = pd.DataFrame(events)

    # Aggregate per user
    user_features = aggregate_per_user(df)

    # Get bot probabilities
    results_df = bot_probabilities(user_features)

    # Split user_id, metadata, and probability
    response_list = []
    for _, row in results_df.iterrows():
        user_id = row["user_id"]
        prob = row["bot_probability"]

        # Metadata: all other columns except user_id & bot_probability
        metadata = row.drop(labels=["user_id", "bot_probability"]).to_dict()

        response_list.append({
            "user_id": user_id,
            "metadata": metadata,
            "bot_probability": prob
        })

    return jsonify(response_list)

@app.route('/admin/categorize-video', methods=['GET'])
def categorize_videos_endpoint():
    """
    CATEGORIZE VIDEO
    This endpoint triggers the video categorization process.
    """
    video_id = request.args.get('video_id')
    try:
        if not video_id:
            return jsonify({"error": "Missing 'video_id' in request body"}), 400
        
        categorize_results = categorize_video_into_3_categories(video_id)
        return jsonify(categorize_results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/admin/evaluate-video', methods=['GET'])
def evaluate_video_endpoint():
    """
    EVALUATE VIDEO QUALITY
    This endpoint triggers the video quality evaluation process.
    """
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({"quality_score": -1.0, "error": "Missing video_id"}), 400

    try:
        quality_score = evaluate_video_quality(video_id)
        return jsonify({"quality_score": float(quality_score)})
    except Exception as e:
        return jsonify({"quality_score": -1.0, "error": str(e)}), 500
    

@app.route('/admin/cluster-videos', methods=['GET'])
def cluster_videos_endpoint():
    """
    CLUSTER VIDEOS
    This endpoint triggers the video clustering process.
    """
    try:
        cluster_videos_into_category()
        
        projected_embeddings = visualize_clustering_algo()
        
        response = {
            "video_embeddings_3d": projected_embeddings[0],
            "centroid_embeddings_3d": projected_embeddings[1]
            
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/evaluate-video-batch', methods=['GET'])
def evaluate_video_endpoint_batch():
    """
    EVALUATE VIDEO QUALITY BATCH
    """
    video_ids = request.args.get('video_ids')
    if not video_ids:
        return jsonify({"error": "Missing video_id"}), 400

    try:
        quality_scores = evaluate_video_quality_batch(video_ids)
        return jsonify(quality_scores)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/admin/visualize-clustering-algo', methods=['GET'])
def visualize_clustering_algo_endpoint():
    """
    CLUSTER VIDEOS
    This endpoint triggers the video clustering process.
    """
    try:
        projected_embeddings = visualize_clustering_algo()
        
        response = {
            "video_embeddings_3d": projected_embeddings[0],
            "centroid_embeddings_3d": projected_embeddings[1]
            
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# This conditional block ensures the web server runs only when the script is executed directly
# The debug=True flag enables the debugger and reloader, which are very useful during development
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6000))  # Render gives $PORT
    app.run(host="0.0.0.0", port=port)