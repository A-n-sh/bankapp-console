import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Home() {
  const [accountId, setAccountId] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  function handleViewAccount(e) {
    e.preventDefault()
    if (!accountId) {
      setError('Please enter an account ID.')
      return
    }
    navigate(`/account/${accountId}`)
  }

  return (
    <div>
      <div className="home-hero">
        <h2>Welcome to Citi Bank</h2>
        <p>Manage your accounts securely and easily</p>
      </div>

      <div className="card">
        <h3>New Customer</h3>
        <p style={{ color: '#888', marginBottom: '18px', fontSize: '14px' }}>Open a Checking or Savings account in seconds.</p>
        <button className="btn btn-primary" style={{ width: '100%' }} onClick={() => navigate('/create-account')}>
          Create Account
        </button>
      </div>

      <div className="divider">or</div>

      <div className="card">
        <h3>Existing Customer</h3>
        <form onSubmit={handleViewAccount}>
          <div className="form-group">
            <label>Account ID</label>
            <input
              type="number"
              placeholder="Enter your account ID"
              value={accountId}
              onChange={e => setAccountId(e.target.value)}
            />
          </div>
          {error && <p className="error">{error}</p>}
          <button className="btn btn-outline" type="submit" style={{ width: '100%' }}>View My Account</button>
        </form>
      </div>
    </div>
  )
}
