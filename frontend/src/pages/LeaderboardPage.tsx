import '../stylesheets/Leaderboard.css'

export function LeaderboardPage() {
    const categories = ["Cooking", "Gaming", "Sports", "Music", "Travel", "Beauty"];
  
    return (
        <div>
            <h2> Select A Category </h2>
            <div className="categories-container">
                {categories.map((cat) => (
                <div key={cat} className="category-box">
                    {cat}
                </div>
                ))}
            </div>

        </div>
    );
  }
  