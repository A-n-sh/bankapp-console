import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const API = 'http://localhost:8080'

export default function CreateAccount() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [accountType, setAccountType] = useState('CHECKING')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const userRes = await fetch(`${API}/api/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email }),
      })
      const user = await userRes.json()
      if (!userRes.ok) {
        setError(user.error)
        setLoading(false)
        return
      }

      const accRes = await fetch(`${API}/api/accounts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId: user.userId, accountType }),
      })
      const account = await accRes.json()
      if (!accRes.ok) {
        setError(account.error)
        setLoading(false)
        return
      }

      navigate(`/account/${account.accountId}`)
    } catch {
      setError('Could not connect to server. Make sure the API is running.')
      setLoading(false)
    }
  }

  return (
    <div>
      <button className="back-link" onClick={() => navigate('/')}>← Back</button>
      <h2>Open an Account</h2>
      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Full Name</label>
            <input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. John Smith" required />
          </div>
          <div className="form-group">
            <label>Email Address</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="e.g. john@example.com" required />
          </div>
          <div className="form-group">
            <label>Account Type</label>
            <select value={accountType} onChange={e => setAccountType(e.target.value)}>
              <option value="CHECKING">Checking — up to $100 overdraft</option>
              <option value="SAVINGS">Savings — no overdraft</option>
            </select>
          </div>
          {error && <p className="error">{error}</p>}
          <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: '100%', padding: '13px' }}>
            {loading ? 'Creating Account...' : 'Open Account'}
          </button>
        </form>
      </div>
    </div>
  )
}
