import { useEffect, useState } from 'react'
import { fetchUserVideosMock, type VideoSummary } from './mockRevenue'
import '../../stylesheets/Revenue.css'

export function RevenueOverviewPage(props: { onSelectVideo: (videoId: string) => void }) {
  const { onSelectVideo } = props
  const [videos, setVideos] = useState<VideoSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      try {
        const data = await fetchUserVideosMock()
        if (!cancelled) setVideos(data)
      } catch (e: any) {
        if (!cancelled) setError(e?.message ?? 'Failed to load videos')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [])

  if (loading) return <div></div>
  if (error) return <div style={{ color: 'tomato' }}>Error: {error}</div>

  return (
    <div>
      <h2>Revenue</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {videos.map(v => (
          <button key={v.videoId} onClick={() => onSelectVideo(v.videoId)} className='revenue_container'>
            <img src={v.thumbnailUrl} alt="thumbnail" width={120} height={120} style={{ objectFit: 'cover', borderRadius: 8 }} />
            <div style={{ display: 'flex', flexDirection: 'column', color: '#fff', fontSize: 16 }}>
              <div style={{ fontWeight: 600 }}>{v.title}</div>
              <div style={{ opacity: 0.85, marginTop: 8 }}>Revenue: ${v.totalRevenue.toFixed(2)}</div>
              <div style={{ opacity: 0.85, marginTop: 6, display: 'flex', gap: 12 }}>
                <span>Views: {v.views.toLocaleString()}</span>
                <span>Likes: {v.likes.toLocaleString()}</span>
                <span>Comments: {v.comments.toLocaleString()}</span>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}


