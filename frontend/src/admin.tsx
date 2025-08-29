import React from 'react'
import { createRoot } from 'react-dom/client'
import './App.css'
import { AdminPage } from './pages/admin/AdminPage'

const container = document.getElementById('root')!
createRoot(container).render(
  <React.StrictMode>
    <div className="Layout" style={{ background: '#000', minHeight: '100vh' }}>
      <div className="ContentArea">
        <AdminPage />
      </div>
    </div>
  </React.StrictMode>
)


