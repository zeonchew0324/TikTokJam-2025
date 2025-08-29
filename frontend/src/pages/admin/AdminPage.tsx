import { useState } from 'react'
import { BotWatchTab } from './BotWatchTab'
import { CreatorFundTab } from './CreatorFundTab'

type AdminTab = 'bot-watch' | 'creator-fund'

export function AdminPage() {
  const [tab, setTab] = useState<AdminTab>('bot-watch')

  return (
    <div style={{ color: '#fff' }}>
      <h2 style={{ marginTop: 0 }}>Admin Control Panel</h2>
      <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
        <button
          onClick={() => setTab('bot-watch')}
          style={{
            padding: '8px 12px',
            borderRadius: 8,
            border: '1px solid ' + (tab === 'bot-watch' ? '#25F4EE' : 'rgba(255,255,255,0.15)'),
            background: '#121212',
            color: tab === 'bot-watch' ? '#fff' : 'rgba(255,255,255,0.85)',
            boxShadow: tab === 'bot-watch' ? '0 0 0 2px rgba(37,244,238,0.2) inset' : 'none'
          }}
        >
          Bot Watch
        </button>
        <button
          onClick={() => setTab('creator-fund')}
          style={{
            padding: '8px 12px',
            borderRadius: 8,
            border: '1px solid ' + (tab === 'creator-fund' ? '#25F4EE' : 'rgba(255,255,255,0.15)'),
            background: '#121212',
            color: tab === 'creator-fund' ? '#fff' : 'rgba(255,255,255,0.85)',
            boxShadow: tab === 'creator-fund' ? '0 0 0 2px rgba(37,244,238,0.2) inset' : 'none'
          }}
        >
          Creator Fund
        </button>
      </div>

      {tab === 'bot-watch' ? <BotWatchTab /> : <CreatorFundTab />}
    </div>
  )
}


