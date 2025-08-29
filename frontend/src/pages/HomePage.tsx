import { useState, useEffect, useRef } from "react"

// Mock comment data
type Comment = {
  id: string;
  username: string;
  avatarUrl: string;
  text: string;
  likes: number;
  timestamp: string;
}

const mockComments: Comment[][] = Array(10).fill(0).map(() => [
  {
    id: '1',
    username: 'tiktok_user123',
    avatarUrl: 'https://picsum.photos/id/237/200',
    text: 'This is amazing! 🔥',
    likes: 1243,
    timestamp: '2d'
  },
  {
    id: '2',
    username: 'viral_clips',
    avatarUrl: 'https://picsum.photos/id/1/200',
    text: 'How did you make this? Tutorial please!',
    likes: 892,
    timestamp: '1d'
  },
  {
    id: '3',
    username: 'content_queen',
    avatarUrl: 'https://picsum.photos/id/65/200',
    text: 'Love the vibes ❤️',
    likes: 2156,
    timestamp: '5h'
  },
  {
    id: '4',
    username: 'trend_follower',
    avatarUrl: 'https://picsum.photos/id/433/200',
    text: 'Can you do a collab?',
    likes: 324,
    timestamp: '3h'
  },
  {
    id: '5',
    username: 'music_lover',
    avatarUrl: 'https://picsum.photos/id/634/200',
    text: 'What song is this? Need it in my playlist right now!',
    likes: 1785,
    timestamp: '1h'
  }
])

export function HomePage(props: { videos?: string[] }) {
  const { videos = [] } = props
  const [likes, setLikes] = useState<number[]>(Array(videos.length).fill(0))
  const [liked, setLiked] = useState<boolean[]>(Array(videos.length).fill(false))
  const [comments, setComments] = useState<number[]>(Array(videos.length).fill(0))
  const [activeCommentSection, setActiveCommentSection] = useState<number | null>(null)
  const [newComment, setNewComment] = useState('')
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
    setActiveCommentSection(prev => (prev === idx ? null : idx));
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

  function addComment(idx: number) {
    if (!newComment.trim()) return
    
    // In a real app, you would post this to your backend
    console.log(`Adding comment to video ${idx}: ${newComment}`)
    
    // Add comment count
    setComments(prev => {
      const newComments = [...prev]
      newComments[idx]++
      return newComments
    })
    
    // Clear input
    setNewComment('')
  }

  // Handle clicking outside comment section to close it
  const commentSectionRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (commentSectionRef.current && !commentSectionRef.current.contains(event.target as Node)) {
        setActiveCommentSection(null)
      }
    }
    
    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  // Refs for all video elements
  const videoRefs = useRef<(HTMLVideoElement | null)[]>([])

  useEffect(() => {
    const observers: IntersectionObserver[] = []
    videoRefs.current.forEach((video, idx) => {
      if (!video) return
      const observer = new window.IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            // Play video when it comes into view
            video.play()
              .then(() => {
                // Once playing, unmute
                video.muted = false;
              })
              .catch((error) => {
                // Handle autoplay restrictions
                console.log("Autoplay prevented:", error);
                // Keep video muted if autoplay is restricted
                video.muted = true;
                video.play().catch(() => {});
              });
          } else {
            // Pause and reset when out of view
            video.pause();
            video.currentTime = 0;
            // Mute for next visibility
            video.muted = true;
          }
        },
        { 
          threshold: 0.7,  // Increased threshold for better detection
          rootMargin: "-10% 0px" // Only trigger when video is well in view
        }
      )
      observer.observe(video)
      observers.push(observer)
    })
    return () => {
      observers.forEach((observer, idx) => {
        if (videoRefs.current[idx]) observer.unobserve(videoRefs.current[idx]!)
        observer.disconnect()
      })
    }
  }, [videos])

  return (
    <div>
      {videos.length === 0 ? (
        <h3>No videos uploaded yet. Go to "Upload Video" to add your first video!</h3>
      ) : (
        <div className="VerticalFeed" style={{ paddingRight: activeCommentSection !== null ? '380px' : '0' }}>
          {videos.map((src, idx) => (
            <div 
              key={idx} 
              className={`VerticalFeed__item ${activeCommentSection === idx ? 'with-comment-section' : ''}`}
              style={{ position: 'relative' }}
            >
              <video
                className="VerticalFeed__video"
                src={src}
                ref={el => (videoRefs.current[idx] = el)}
                playsInline
                preload="auto"
                muted
                loop
                onClick={(e) => {
                  // Toggle play/pause on video click
                  const video = e.currentTarget as HTMLVideoElement;
                  if (video.paused) {
                    video.play();
                  } else {
                    video.pause();
                  }
                }}
              />
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
                  className={`ActionBar__btn${activeCommentSection === idx ? ' active' : ''}`}
                  aria-label="Comment"
                  onClick={(e) => {
                    e.stopPropagation(); // Prevent event from bubbling to parent
                    toggleComments(idx);
                  }}
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
              
              {/* Comment Section */}
              {activeCommentSection === idx && (
                <div className="CommentSection" ref={commentSectionRef}>
                  <div className="CommentSection__header">
                    <h3>Comments ({comments[idx]})</h3>
                    <button 
                      className="CommentSection__close" 
                      onClick={() => setActiveCommentSection(null)}
                    >
                      ✕
                    </button>
                  </div>
                  
                  <div className="CommentSection__list">
                    {mockComments[idx % mockComments.length].map((comment) => (
                      <div key={comment.id} className="Comment">
                        <img 
                          src={comment.avatarUrl} 
                          alt={comment.username}
                          className="Comment__avatar" 
                        />
                        <div className="Comment__content">
                          <div className="Comment__username">{comment.username}</div>
                          <div className="Comment__text">{comment.text}</div>
                          <div className="Comment__meta">
                            <span>{comment.timestamp}</span>
                            <button className="Comment__like">
                              ♥ {comment.likes}
                            </button>
                            <button className="Comment__reply">Reply</button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="CommentSection__compose">
                    <input
                      type="text"
                      placeholder="Add comment..."
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && addComment(idx)}
                    />
                    <button 
                      className="CommentSection__post"
                      onClick={() => addComment(idx)}
                      disabled={!newComment.trim()}
                    >
                      Post
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
  