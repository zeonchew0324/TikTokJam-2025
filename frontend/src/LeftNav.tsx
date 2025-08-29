type NavKey = 'home' | 'upload' | 'leaderboard' | 'revenue' | 'admin'
import './stylesheets/Navbar.css'

export function LeftNav(props: { current: NavKey; onChange: (k: NavKey) => void; collapsed?: boolean; onToggle?: () => void }) {
  const { current, onChange, collapsed, onToggle } = props
  return (
    <div className={"LeftNav" + (collapsed ? ' is-collapsed' : '')}>
      <button className="LeftNav__toggle" onClick={onToggle}>{collapsed ? '»' : '«'}</button>
      <div className={`LeftNav__item ${current === 'home' ? 'is-active' : ''}`} onClick={() => onChange('home')}>
        <span className="material-symbols-outlined">home</span>
        <span className="LeftNav__label">Home</span>
      </div>
      <div className={`LeftNav__item ${current === 'upload' ? 'is-active' : ''}`} onClick={() => onChange('upload')}>
        <span className="material-symbols-outlined">upload</span>
        <span className="LeftNav__label">Upload Video</span>
      </div>
      <div className={`LeftNav__item ${current === 'leaderboard' ? 'is-active' : ''}`} onClick={() => onChange('leaderboard')}>
        <span className="material-symbols-outlined">leaderboard</span>
        <span className="LeftNav__label">Leaderboard</span>
      </div>
      <div className={`LeftNav__item ${current === 'revenue' ? 'is-active' : ''}`} onClick={() => onChange('revenue')}>
        <span className="material-symbols-outlined">attach_money</span>
        <span className="LeftNav__label">Revenue</span>
      </div>
      <div className={`LeftNav__item ${current === 'admin' ? 'is-active' : ''}`} onClick={() => onChange('admin')}>
        <span className="material-symbols-outlined">admin_panel_settings</span>
        <span className="LeftNav__label">Admin</span>
      </div>
    </div>
  )
}


