import { useCallback, useEffect, useState } from 'react'
import './App.css'
import { LeftNav } from './LeftNav'
import { HomePage, UploadVideoPage, LeaderboardPage } from './pages'

export function App() {
  const [route, setRoute] = useState<'home' | 'upload' | 'leaderboard'>('home')

  return (
    <div className="Layout">
      <LeftNav current={route} onChange={setRoute} />
      <div className="ContentArea">
        {route === 'home' && <HomePage />}
        {route === 'upload' && <UploadVideoPage />}
        {route === 'leaderboard' && <LeaderboardPage />}
      </div>
    </div>
  )
}
