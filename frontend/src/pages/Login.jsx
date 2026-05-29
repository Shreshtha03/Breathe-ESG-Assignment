import React, { useState } from 'react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || ''

export default function Login({ onLogin }) {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        try {
            // Django session auth via CSRF-free basic auth
            const response = await axios.get(`${API_BASE}/api/records/`, {
                auth: { username, password },
                params: { page_size: 1 }
            })
            if (response.status === 200) {
                onLogin(username)
            }
        } catch (err) {
            setError('Invalid credentials or server unreachable')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="login-wrapper">
            <div className="login-box">
                <div className="login-logo">
                    <div className="logo-icon">🌿</div>
                    <h1>Breathe ESG</h1>
                    <p>Emissions Data Ingestion Platform</p>
                </div>

                <form onSubmit={handleSubmit}>
                    <p style={{ fontWeight: 600, marginBottom: '1.25rem', fontSize: '1.1rem' }}>Analyst Sign In</p>

                    <div className="form-group">
                        <label>Username</label>
                        <div className="input-wrap">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>
                            <input
                                type="text"
                                value={username}
                                onChange={e => setUsername(e.target.value)}
                                placeholder="analyst"
                                required
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Password</label>
                        <div className="input-wrap">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" /></svg>
                            <input
                                type="password"
                                value={password}
                                onChange={e => setPassword(e.target.value)}
                                placeholder="••••••••••"
                                required
                            />
                        </div>
                    </div>

                    {error && (
                        <div className="error-msg">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" /></svg>
                            {error}
                        </div>
                    )}

                    <button type="submit" className="btn-primary" disabled={loading}>
                        {loading ? <><span className="spinner" style={{ marginRight: '0.5rem' }} /> Signing in...</> : 'Continue to Dashboard'}
                    </button>
                </form>

                <div className="login-footer">RESTRICTED ACCESS SYSTEM</div>
            </div>
        </div>
    )
}
