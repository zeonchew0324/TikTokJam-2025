import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import classification_report, confusion_matrix

# ----------------------
# Load model & scaler
# ----------------------
scaler = joblib.load("ai/bot_detection/models/scaler.pkl")
iso_model = joblib.load("ai/bot_detection/models/isolation_forest_model.pkl")

# ----------------------
# Aggregation function (same as training)
# ----------------------
def aggregate_per_user(df):
    agg_funcs = {
        "video_id": pd.Series.nunique,  # num_videos_engaged
        "event_id": "count",            # total_events
        "engagement_duration": "mean",  # avg_engagement_duration
        "account_age_days": "first",
        "followers_count": "first",
        "following_count": "first",
        "profile_pic": "first",
        "bio_length": "first",
        "verified": "first",
        "location_consistent": "first",
        "timezone_offset": "first",
    }

    # Include 'is_bot' only if present in dataset
    if "is_bot" in df.columns:
        agg_funcs["is_bot"] = "first"

    user_df = df.groupby("user_id").agg(agg_funcs).reset_index()
    user_df = user_df.rename(columns={
        "video_id": "num_videos_engaged",
        "event_id": "total_events",
        "engagement_duration": "avg_engagement_duration"
    })

    # Feature engineering
    user_df["followers_following_ratio"] = (
        user_df["followers_count"] / (user_df["following_count"] + 1)
    )

    return user_df

# ----------------------
# Bot probability function
# ----------------------
def bot_probability(features_df):
    """Return bot probability for each user in features_df."""
    # Drop label and ID before scaling
    X = features_df.drop(columns=["user_id"], errors="ignore")

    # Scale features
    X_scaled = scaler.transform(X)

    # IsolationForest: higher scores = more normal, lower = anomalous
    scores = iso_model.decision_function(X_scaled)

    # Normalize to [0,1] as probability of being a bot
    prob = 1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-9)

    return prob

# ----------------------
# Bot probability function
# ----------------------
def bot_probabilities(user_df: pd.DataFrame) -> pd.DataFrame:
    # Drop ID/label columns
    X = user_df.drop(columns=["user_id"], errors="ignore")

    # Scale features
    X_scaled = scaler.transform(X)

    # IsolationForest scores
    scores = iso_model.decision_function(X_scaled)

    # Normalize to [0,1] probability of being a bot
    probs = 1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-9)

    # Add probability column
    user_df["bot_probability"] = probs

    # Filter suspicious users
    suspicious = user_df[user_df["bot_probability"] > 0.5]

    # Sort by probability (descending, most suspicious first)
    suspicious = suspicious.sort_values("bot_probability", ascending=False)

    # Limit to top 10
    suspicious = suspicious.head(10)

    return suspicious.reset_index(drop=True)

# ----------------------
# Main evaluation
# ----------------------
if __name__ == "__main__":
    # Load raw test events
    test_df = pd.read_csv("datasets/test_skibidi.csv")

    # Aggregate per user
    test_users = aggregate_per_user(test_df)

    # Compute probabilities
    probs = bot_probability(test_users)

    # Convert to binary prediction (threshold = 0.5 by default)
    y_pred = (probs >= 0.6).astype(int)
    y_true = test_users["is_bot"].values

    # Evaluate
    print("Confusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, digits=3))

    # Optional: save per-user predictions with probability
    results = test_users[["user_id", "is_bot"]].copy()
    results["bot_probability"] = probs
    results["prediction"] = y_pred
    results.to_csv("test_predictions.csv", index=False)
    print("\n✅ Results saved to test_predictions.csv")
