import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import './index.css'

function App() {
    const [user, setUser] = useState(() => {
        return sessionStorage.getItem('breathe_user') || null
    })

    const handleLogin = (username, password) => {
        sessionStorage.setItem('breathe_user', username)
        sessionStorage.setItem('breathe_pass', password)
        setUser(username)
    }

    const handleLogout = () => {
        sessionStorage.removeItem('breathe_user')
        sessionStorage.removeItem('breathe_pass')
        setUser(null)
    }

    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={
                    user ? <Navigate to="/" /> : <Login onLogin={handleLogin} />
                } />
                <Route path="/*" element={
                    user ? <Dashboard user={user} onLogout={handleLogout} /> : <Navigate to="/login" />
                } />
            </Routes>
        </BrowserRouter>
    )
}

export default App
