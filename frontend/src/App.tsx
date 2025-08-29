import { useCallback, useEffect, useState } from 'react'
import './App.css'
import { LeftNav } from './LeftNav'
import { HomePage } from './pages/HomePage'
import { LeaderboardPage } from './pages/LeaderboardPage'
import { UploadVideoPage } from './pages/UploadVideoPage'
import { RevenueOverviewPage } from './pages/revenue/RevenueOverviewPage'
import { VideoAnalyticsPage } from './pages/revenue/VideoAnalyticsPage'


export function App() {
  const [route, setRoute] = useState<'home' | 'upload' | 'leaderboard' | 'revenue' | { name: 'video-analytics', videoId: string }>('home')
  const [collapsed, setCollapsed] = useState(false)
  const [uploadedVideos, setUploadedVideos] = useState<string[]>([])

  function handleVideoUploaded(url: string) {
    setUploadedVideos(prev => [url, ...prev])
    setRoute('home')
  }

  return (
    <div className="Layout">
      <LeftNav current={typeof route === 'string' ? route : 'revenue'} onChange={setRoute as any} collapsed={collapsed} onToggle={() => setCollapsed(v => !v)} />
      <div className="ContentArea">
        {route === 'home' && <HomePage videos={uploadedVideos} />}
        {route === 'upload' && <UploadVideoPage onUploaded={handleVideoUploaded} />}
        {route === 'leaderboard' && <LeaderboardPage />}
        {route === 'revenue' && (
          <RevenueOverviewPage onSelectVideo={(videoId) => setRoute({ name: 'video-analytics', videoId })} />
        )}
        {typeof route === 'object' && route.name === 'video-analytics' && (
          <VideoAnalyticsPage videoId={route.videoId} onBack={() => setRoute('revenue')} />
        )}
      </div>
    </div>
  )
}
