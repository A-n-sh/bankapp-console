import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

const API = 'http://localhost:8080'

export default function TransactionHistory() {
  const { accountId } = useParams()
  const [transactions, setTransactions] = useState([])
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    fetch(`${API}/api/accounts/${accountId}/transactions`)
      .then(res => res.json())
      .then(data => {
        if (data.error) setError(data.error)
        else setTransactions(data)
      })
      .catch(() => setError('Could not connect to server.'))
  }, [accountId])

  return (
    <div>
      <button className="back-link" onClick={() => navigate(`/account/${accountId}`)}>← Back</button>
      <div className="page-header">
        <h2>Transaction History</h2>
        <span style={{ fontSize: '13px', color: '#888' }}>{transactions.length} transaction{transactions.length !== 1 ? 's' : ''}</span>
      </div>
      <div className="card">
        {error && <p className="error">{error}</p>}
        {!error && transactions.length === 0 && (
          <div className="empty-state">No transactions yet.</div>
        )}
        {transactions.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Amount</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map(t => {
                const isDeposit = t.type === 'DEPOSIT'
                return (
                  <tr key={t.txnId}>
                    <td style={{ color: '#aaa', fontSize: '13px' }}>#{t.txnId}</td>
                    <td>
                      <span className={`txn-type ${isDeposit ? 'deposit' : 'withdrawal'}`}>
                        {isDeposit ? '+ Deposit' : '− Withdrawal'}
                      </span>
                    </td>
                    <td className={`txn-amount ${isDeposit ? 'deposit' : 'withdrawal'}`}>
                      {isDeposit ? '+' : '-'}${t.amount.toFixed(2)}
                    </td>
                    <td style={{ color: '#888', fontSize: '13px' }}>{t.date}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
