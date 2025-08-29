import { useState } from "react"

export function HomePage(props: { videos?: string[] }) {
  const { videos = [] } = props
  const [likes, setLikes] = useState<number[]>(Array(videos.length).fill(0))
  return (
    <div>
      <h2>Home</h2>
      {videos.length === 0 ? (
        <p>Welcome!</p>
      ) : (
        <div className="VerticalFeed">
          {videos.map((src, idx) => (
            <div key={idx} className="VerticalFeed__item" style={{ position: 'relative' }}>
              <video className="VerticalFeed__video" src={src} controls />
              <div className="ActionBar" style={{
                position: 'absolute',
                right: 16,
                bottom: 32,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 20,
                zIndex: 2
              }}>
                <button className="ActionBar__btn" aria-label="Like" style={{ background: 'none', border: 'none', color: 'white', fontSize: 24, cursor: 'pointer' }}>
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor"><path d="M7.5 2.25C10.5 2.25 12 4.25 12 4.25C12 4.25 13.5 2.25 16.5 2.25C20 2.25 22.5 4.99999 22.5 8.5C22.5 12.5 19.2311 16.0657 16.25 18.75C14.4095 20.4072 13 21.5 12 21.5C11 21.5 9.55051 20.3989 7.75 18.75C4.81949 16.0662 1.5 12.5 1.5 8.5C1.5 4.99999 4 2.25 7.5 2.25Z"></path></svg>
                  <div style={{ fontSize: 14, marginTop: 4 }}>192.5K</div>
                </button>
                <button className="ActionBar__btn" aria-label="Comment" style={{ background: 'none', border: 'none', color: 'white', fontSize: 24, cursor: 'pointer' }}>
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor"><path d="M12 3C6.48 3 2 6.58 2 11c0 2.08 1.06 3.97 2.83 5.36-.13.44-.51 1.54-.7 2.09-.11.3.19.57.48.45.66-.27 1.98-.81 2.8-1.15C9.18 17.91 10.56 18 12 18c5.52 0 10-3.58 10-8s-4.48-7-10-7z"></path></svg>
                  <div style={{ fontSize: 14, marginTop: 4 }}>2319</div>
                </button>
                <button className="ActionBar__btn" aria-label="Share" style={{ background: 'none', border: 'none', color: 'white', fontSize: 24, cursor: 'pointer' }}>
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor"><path d="M18 8.59l-1.41-1.42L12 11.76 7.41 7.17 6 8.59l6 6z"></path></svg>
                  <div style={{ fontSize: 14, marginTop: 4 }}>8211</div>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
  