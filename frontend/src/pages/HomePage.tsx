export function HomePage(props: { videos?: string[] }) {
  const { videos = [] } = props
  return (
    <div>
      <h2>Home</h2>
      {videos.length === 0 ? (
        <p>Welcome!</p>
      ) : (
        <div className="VerticalFeed">
          {videos.map((src, idx) => (
            <div key={idx} className="VerticalFeed__item">
              <video className="VerticalFeed__video" src={src} controls />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
  