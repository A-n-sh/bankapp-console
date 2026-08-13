import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

const API = 'http://localhost:8080'

export default function Withdraw() {
  const { accountId } = useParams()
  const [amount, setAmount] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setMessage('')

    try {
      const res = await fetch(`${API}/api/accounts/${accountId}/withdraw`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount: parseFloat(amount) }),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.error)
      } else {
        setMessage(`Withdrew $${parseFloat(amount).toFixed(2)}. New balance: $${data.balance.toFixed(2)}`)
        setAmount('')
      }
    } catch {
      setError('Could not connect to server.')
    }
  }

  return (
    <div>
      <button className="back-link" onClick={() => navigate(`/account/${accountId}`)}>← Back</button>
      <h2>Withdraw Funds</h2>
      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Amount</label>
            <div className="amount-input-wrap">
              <span className="currency-symbol">$</span>
              <input
                type="number"
                min="0.01"
                step="0.01"
                placeholder="0.00"
                value={amount}
                onChange={e => setAmount(e.target.value)}
                required
              />
            </div>
          </div>
          {error && <p className="error">{error}</p>}
          {message && <p className="success">{message}</p>}
          <div className="btn-group">
            <button className="btn btn-danger" type="submit" style={{ flex: 1 }}>Confirm Withdrawal</button>
            <button className="btn btn-secondary" type="button" onClick={() => navigate(`/account/${accountId}`)}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  )
}
