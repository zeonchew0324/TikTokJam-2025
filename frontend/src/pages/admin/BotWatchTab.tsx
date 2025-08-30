import { useEffect, useMemo, useState } from 'react'
import { mockApiService } from '../../services/mockApiService'
import type { SuspiciousUser } from '../../types/admin'

export function BotWatchTab() {
  const [isScanning, setIsScanning] = useState(false)
  const [status, setStatus] = useState<'idle' | 'scanning' | 'complete'>('idle')
  const [users, setUsers] = useState<SuspiciousUser[]>([])
  const [confirmUserId, setConfirmUserId] = useState<string | null>(null)
  const [toast, setToast] = useState<string | null>(null)

  async function handleRunScan() {
    setIsScanning(true)
    setStatus('scanning')
    await mockApiService.runBotScan()
    const data = await mockApiService.getSuspiciousUsers()
    setUsers(data)
    setIsScanning(false)
    setStatus('complete')

    // try {
    //   // Assume backend endpoint is /api/admin/bot-scan (POST triggers scan, GET fetches results)
    //   await fetch('/api/admin/bot-scan', { method: 'POST' })
    //   const resp = await fetch('/api/admin/bot-scan', { method: 'GET' })
    //   if (!resp.ok) throw new Error('Failed to fetch suspicious users')
    //   const data = await resp.json()
    //   setUsers(data)
    // } catch (err) {
    //   setToast('Failed to fetch suspicious users')
    // } finally {
    //   setIsScanning(false)
    //   setStatus('complete')
    // }
  }

  function confirmBan(userId: string) {
    setConfirmUserId(userId)
  }

  function performBan() {
    if (!confirmUserId) return
    setUsers(prev => prev.filter(u => u.userId !== confirmUserId))
    setConfirmUserId(null)
    setToast('User banned successfully')
  }

  useEffect(() => {
    if (!toast) return
    const t = setTimeout(() => setToast(null), 2000)
    return () => clearTimeout(t)
  }, [toast])

  const statusLabel = useMemo(() => {
    if (status === 'idle') return 'Idle'
    if (status === 'scanning') return 'Scanning...'
    return 'Complete'
  }, [status])

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <div>
          <div style={{ fontSize: 18, fontWeight: 600 }}>Manual Scan Controls</div>
          <div style={{ color: 'rgba(255,255,255,0.7)' }}>Status: {statusLabel}</div>
        </div>
        <button
          onClick={handleRunScan}
          disabled={isScanning}
          style={{
            padding: '10px 14px', borderRadius: 10, border: '1px solid #25F4EE', background: isScanning ? '#0f0f0f' : '#121212',
            color: '#fff', cursor: isScanning ? 'not-allowed' : 'pointer', display: 'inline-flex', alignItems: 'center', gap: 8
          }}
        >
          {isScanning && <span className="material-symbols-outlined" style={{ animation: 'spin 1s linear infinite' }}>progress_activity</span>}
          Run Random Check
        </button>
      </div>

      <div style={{ marginTop: 16 }}>
        <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>Suspicious Users for Review</div>
        <div style={{ overflowX: 'auto', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#181818', textAlign: 'left' }}>
                <th style={{ padding: 12 }}>User</th>
                <th style={{ padding: 12 }}>Suspicion Score</th>
                <th style={{ padding: 12 }}>Reason for Flag</th>
                <th style={{ padding: 12 }}>Detected On</th>
                <th style={{ padding: 12 }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.userId} style={{ borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                  <td style={{ padding: 12, display: 'flex', alignItems: 'center', gap: 10 }}>
                    <img src={u.avatarUrl} alt={u.username} style={{ width: 36, height: 36, borderRadius: '50%' }} />
                    <div>
                      <div style={{ fontWeight: 600 }}>{u.username}</div>
                      <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.6)' }}>{u.userId}</div>
                    </div>
                  </td>
                  <td style={{ padding: 12 }}>{u.suspicionScore}</td>
                  <td style={{ padding: 12 }}>{u.reason}</td>
                  <td style={{ padding: 12 }}>{new Date(u.detectedAt).toLocaleString()}</td>
                  <td style={{ padding: 12 }}>
                    <button
                      onClick={() => confirmBan(u.userId)}
                      style={{ padding: '6px 10px', borderRadius: 8, border: '1px solid #FE2C55', background: 'transparent', color: '#FE2C55' }}
                    >
                      Ban User
                    </button>
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr>
                  <td colSpan={5} style={{ padding: 16, color: 'rgba(255,255,255,0.6)' }}>No data. Run a scan to populate results.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div style={{ marginTop: 24 }}>
        <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>Automated Spam Network Detections</div>
        <div style={{ color: 'rgba(255,255,255,0.6)' }}>Coming soon in this prototype.</div>
      </div>

      {confirmUserId && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#151515', border: '1px solid rgba(255,255,255,0.12)', padding: 20, borderRadius: 12, width: 360 }}>
            <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>Confirm Ban</div>
            <div style={{ color: 'rgba(255,255,255,0.8)', marginBottom: 16 }}>Are you sure you want to ban this user?</div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <button onClick={() => setConfirmUserId(null)} style={{ padding: '6px 10px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.2)', background: 'transparent', color: '#fff' }}>Cancel</button>
              <button onClick={performBan} style={{ padding: '6px 10px', borderRadius: 8, border: '1px solid #FE2C55', background: '#FE2C55', color: '#fff' }}>Ban</button>
            </div>
          </div>
        </div>
      )}

      {toast && (
        <div style={{ position: 'fixed', bottom: 24, right: 24, background: '#1f1f1f', border: '1px solid rgba(255,255,255,0.12)', padding: '10px 14px', borderRadius: 10 }}>
          {toast}
        </div>
      )}

      <style>{`@keyframes spin { from { transform: rotate(0deg) } to { transform: rotate(360deg) } }`}</style>
    </div>
  )
}


