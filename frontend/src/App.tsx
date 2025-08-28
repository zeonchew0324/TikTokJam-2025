import { useCallback, useEffect, useState } from 'react'
import './App.css'
import { LeftNav } from './LeftNav'
import { HomePage } from './pages/HomePage'
import { LeaderboardPage } from './pages/LeaderboardPage'
import { UploadVideoPage } from './pages/UploadVideoPage'


export function App() {
  const [route, setRoute] = useState<'home' | 'upload' | 'leaderboard'>('home')
  const [collapsed, setCollapsed] = useState(false)
  const [uploadedVideos, setUploadedVideos] = useState<string[]>([])

  function handleVideoUploaded(url: string) {
    setUploadedVideos(prev => [url, ...prev])
    setRoute('home')
  }

  return (
    <div className="Layout">
      <LeftNav current={route} onChange={setRoute} collapsed={collapsed} onToggle={() => setCollapsed(v => !v)} />
      <div className="ContentArea">
        {route === 'home' && <HomePage videos={uploadedVideos} />}
        {route === 'upload' && <UploadVideoPage onUploaded={handleVideoUploaded} />}
        {route === 'leaderboard' && <LeaderboardPage />}
      </div>
    </div>
  )
}
