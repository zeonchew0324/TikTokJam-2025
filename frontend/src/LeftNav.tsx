type NavKey = 'home' | 'upload' | 'leaderboard'

export function LeftNav(props: { current: NavKey; onChange: (k: NavKey) => void }) {
  const { current, onChange } = props
  return (
    <div className="LeftNav">
      <div className={`LeftNav__item ${current === 'home' ? 'is-active' : ''}`} onClick={() => onChange('home')}>
        Home
      </div>
      <div className={`LeftNav__item ${current === 'upload' ? 'is-active' : ''}`} onClick={() => onChange('upload')}>
        Upload Video
      </div>
      <div className={`LeftNav__item ${current === 'leaderboard' ? 'is-active' : ''}`} onClick={() => onChange('leaderboard')}>
        Leaderboard
      </div>
    </div>
  )
}


