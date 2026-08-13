import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import CreateAccount from './pages/CreateAccount'
import AccountDetails from './pages/AccountDetails'
import Deposit from './pages/Deposit'
import Withdraw from './pages/Withdraw'
import TransactionHistory from './pages/TransactionHistory'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <header>
          <div>
            <h1>CITI BANK</h1>
            <div className="header-subtitle">Online Banking</div>
          </div>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/create-account" element={<CreateAccount />} />
            <Route path="/account/:accountId" element={<AccountDetails />} />
            <Route path="/account/:accountId/deposit" element={<Deposit />} />
            <Route path="/account/:accountId/withdraw" element={<Withdraw />} />
            <Route path="/account/:accountId/transactions" element={<TransactionHistory />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
