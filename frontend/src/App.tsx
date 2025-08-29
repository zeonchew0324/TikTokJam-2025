import { useCallback, useEffect, useState } from 'react'
import './App.css'
import { LeftNav } from './LeftNav'
import { HomePage } from './pages/HomePage'
import { UploadVideoPage } from './pages/UploadVideoPage'
import { RevenueOverviewPage } from './pages/revenue/RevenueOverviewPage'
import { VideoAnalyticsPage } from './pages/revenue/VideoAnalyticsPage'
import { AdminPage } from './pages/admin/AdminPage'

export type UploadedVideo = {
  id: string;
  url: string;
  title: string;
  description: string;
  creator: string;
  hashtags: string[];
}

export function App() {
  const [route, setRoute] = useState<'home' | 'upload' | 'leaderboard' | 'revenue' | 'admin' | { name: 'video-analytics', videoId: string }>('home')
  const [collapsed, setCollapsed] = useState(false)
  const [uploadedVideos, setUploadedVideos] = useState<UploadedVideo[]>([])

  function handleVideoUploaded(video: UploadedVideo) {
    setUploadedVideos(prev => [video, ...prev])
    setRoute('home')
  }

  return (
    <div className="Layout">
      <LeftNav current={typeof route === 'string' ? route : 'revenue'} onChange={setRoute as any} collapsed={collapsed} onToggle={() => setCollapsed(v => !v)} />
      <div className="ContentArea">
        {route === 'home' && <HomePage videos={uploadedVideos} />}
        {route === 'upload' && <UploadVideoPage onUploaded={handleVideoUploaded} />}
        {route === 'revenue' && (
          <RevenueOverviewPage onSelectVideo={(videoId) => setRoute({ name: 'video-analytics', videoId })} />
        )}
        {route === 'admin' && (
          <AdminPage />
        )}
        {typeof route === 'object' && route.name === 'video-analytics' && (
          <VideoAnalyticsPage videoId={route.videoId} onBack={() => setRoute('revenue')} />
        )}
      </div>
    </div>
  )
}
