import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

const API = 'http://localhost:8080'

export default function AccountDetails() {
  const { accountId } = useParams()
  const [account, setAccount] = useState(null)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    fetch(`${API}/api/accounts/${accountId}`)
      .then(res => res.json())
      .then(data => {
        if (data.error) setError(data.error)
        else setAccount(data)
      })
      .catch(() => setError('Could not connect to server.'))
  }, [accountId])

  if (error) return (
    <div>
      <button className="back-link" onClick={() => navigate('/')}>← Back</button>
      <p className="error">{error}</p>
    </div>
  )

  if (!account) return <p>Loading...</p>

  return (
    <div>
      <button className="back-link" onClick={() => navigate('/')}>← Back</button>

      <div className="balance-card">
        <div className="account-type-badge">{account.accountType} Account</div>
        <div className="balance-label">Current Balance</div>
        <div className="balance-amount">${account.balance.toFixed(2)}</div>
        <div className="account-meta">
          <div className="meta-item">
            <div className="meta-label">Account Holder</div>
            <div className="meta-value">{account.userName}</div>
          </div>
          <div className="meta-item">
            <div className="meta-label">Account ID</div>
            <div className="meta-value">#{account.accountId}</div>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>Quick Actions</h3>
        <div className="action-grid">
          <button className="action-btn deposit" onClick={() => navigate(`/account/${accountId}/deposit`)}>
            <span className="action-icon">↑</span>
            Deposit
          </button>
          <button className="action-btn withdraw" onClick={() => navigate(`/account/${accountId}/withdraw`)}>
            <span className="action-icon">↓</span>
            Withdraw
          </button>
          <button className="action-btn history" onClick={() => navigate(`/account/${accountId}/transactions`)}>
            <span className="action-icon">☰</span>
            History
          </button>
        </div>
      </div>
    </div>
  )
}
