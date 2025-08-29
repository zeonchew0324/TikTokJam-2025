import { useState } from "react"

export function HomePage(props: { videos?: string[] }) {
  const { videos = [] } = props
  const [likes, setLikes] = useState<number[]>(Array(videos.length).fill(0))
  const [liked, setLiked] = useState<boolean[]>(Array(videos.length).fill(false))
  const [comments, setComments] = useState<number[]>(Array(videos.length).fill(0))
  const [commented, setCommented] = useState<boolean[]>(Array(videos.length).fill(false))
  const [shares, setShares] = useState<number[]>(Array(videos.length).fill(0))
  const [shared, setShared] = useState<boolean[]>(Array(videos.length).fill(false))

  function toggleLike(idx: number) {
    setLiked((prev) => {
      const newLiked = [...prev]
      newLiked[idx] = !newLiked[idx]
      return newLiked
    })
    setLikes((prev) => {
      const newLikes = [...prev]
      newLikes[idx] = liked[idx] ? newLikes[idx] - 1 : newLikes[idx] + 1
      return newLikes
    })
  }

  function toggleComments(idx: number) {
    setCommented((prev) => {
      const newCommented = [...prev]
      newCommented[idx] = !newCommented[idx]
      return newCommented
    })

    setComments((prev) => {
      const newComments = [...prev]
      newComments[idx] = commented[idx] ? newComments[idx] - 1 : newComments[idx] + 1
      return newComments
    })
  }

  function toggleShares(idx: number) {
    setShared((prev) => {
      const newShared = [...prev]
      newShared[idx] = !newShared[idx]
      return newShared
    })

    setShares((prev) => {
      const newShares = [...prev]
      newShares[idx] = shared[idx] ? newShares[idx] - 1 : newShares[idx] + 1
      return newShares
    })
  }

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
              <div className="ActionBar" >
                <button
                  className={`ActionBar__btn${liked[idx] ? ' liked' : ''}`}
                  aria-label="Like"
                  onClick={() => toggleLike(idx)}
                >
                  <svg width="28" height="28" viewBox="0 0 24 24" fill={liked[idx] ? '#ff2d55' : 'currentColor'}>
                    <path d="M7.5 2.25C10.5 2.25 12 4.25 12 4.25C12 4.25 13.5 2.25 16.5 2.25C20 2.25 22.5 4.99999 22.5 8.5C22.5 12.5 19.2311 16.0657 16.25 18.75C14.4095 20.4072 13 21.5 12 21.5C11 21.5 9.55051 20.3989 7.75 18.75C4.81949 16.0662 1.5 12.5 1.5 8.5C1.5 4.99999 4 2.25 7.5 2.25Z" />
                  </svg>
                </button>
                <div className="ActionBar_label" style={{ color: liked[idx] ? '#ff2d55' : undefined }}>{likes[idx]}</div>

                {/* Comment Button */}
                <button
                  className="ActionBar__btn"
                  aria-label="Comment"
                  onClick={() => toggleComments(idx)}
                >
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 3C6.48 3 2 6.58 2 11c0 2.08 1.06 3.97 2.83 5.36-.13.44-.51 1.54-.7 2.09-.11.3.19.57.48.45.66-.27 1.98-.81 2.8-1.15C9.18 17.91 10.56 18 12 18c5.52 0 10-3.58 10-8s-4.48-7-10-7z" />
                  </svg>
                </button>
                <div className="ActionBar_label">{comments[idx]}</div>

                {/* Share Button */}
                <button
                  className="ActionBar__btn"
                  aria-label="Share"
                  onClick={() => toggleShares(idx)}
                >
                  <span className="material-symbols-outlined" style={{ fontSize: "32px" }}>
                    share
                  </span>
                </button>
                <div className="ActionBar_label">{shares[idx]}</div>
              </div>
            </div>
          ))} 
        </div>
      )}
    </div>
  )
}
  