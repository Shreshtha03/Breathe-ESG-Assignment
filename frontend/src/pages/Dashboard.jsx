import React, { useState, useEffect, useCallback } from 'react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || ''

const api = axios.create({
    baseURL: API_BASE,
})

api.interceptors.request.use(config => {
    const user = sessionStorage.getItem('breathe_user')
    const pass = sessionStorage.getItem('breathe_pass') || 'analyst123'
    if (user) {
        config.auth = { username: user, password: pass }
    }
    return config
})

const STATUSES = ['all', 'pending', 'flagged', 'approved', 'rejected']
const SOURCES = ['all', 'SAP', 'UTILITY', 'TRAVEL']

export default function Dashboard({ user: username, onLogout }) {
    const [tab, setTab] = useState('records')
    const [records, setRecords] = useState([])
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)
    const [statusFilter, setStatusFilter] = useState('all')
    const [sourceFilter, setSourceFilter] = useState('all')
    const [toast, setToast] = useState(null)
    const [selectedRecord, setSelectedRecord] = useState(null)

    const showToast = (msg, type = 'success') => {
        setToast({ msg, type })
        setTimeout(() => setToast(null), 3000)
    }

    const fetchRecords = useCallback(async () => {
        setLoading(true)
        try {
            const params = {}
            if (statusFilter !== 'all') params.status = statusFilter
            if (sourceFilter !== 'all') params.source_type = sourceFilter
            const res = await api.get('/api/records/', { params })
            setRecords(res.data.results || res.data)
        } catch (e) {
            showToast('Failed to load records', 'error')
        } finally {
            setLoading(false)
        }
    }, [statusFilter, sourceFilter])

    const fetchStats = async () => {
        try {
            const res = await api.get('/api/stats/')
            setStats(res.data)
        } catch (e) { }
    }

    useEffect(() => {
        fetchRecords()
        fetchStats()
    }, [fetchRecords])

    const handleAction = async (id, action) => {
        try {
            await api.post(`/api/records/${id}/${action}/`)
            showToast(`Record ${action}d successfully`)
            fetchRecords()
            fetchStats()
        } catch (e) {
            showToast(`Failed to ${action} record`, 'error')
        }
    }

    return (
        <div className="dashboard-layout">
            <aside className="sidebar">
                <div className="sidebar-brand">
                    <div className="logo-icon" style={{ fontSize: '1.1rem' }}>🌿</div>
                    <span>Breathe ESG</span>
                </div>

                <button className={`nav-item ${tab === 'records' ? 'active' : ''}`} onClick={() => setTab('records')}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><polyline points="10 9 9 9 8 9" /></svg>
                    Review Records
                </button>

                <button className={`nav-item ${tab === 'upload' ? 'active' : ''}`} onClick={() => setTab('upload')}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="16 16 12 12 8 16" /><line x1="12" y1="12" x2="12" y2="21" /><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3" /></svg>
                    Upload Data
                </button>

                <button className={`nav-item ${tab === 'batches' ? 'active' : ''}`} onClick={() => setTab('batches')}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="8" y1="6" x2="21" y2="6" /><line x1="8" y1="12" x2="21" y2="12" /><line x1="8" y1="18" x2="21" y2="18" /><line x1="3" y1="6" x2="3.01" y2="6" /><line x1="3" y1="12" x2="3.01" y2="12" /><line x1="3" y1="18" x2="3.01" y2="18" /></svg>
                    Batches
                </button>

                <div className="sidebar-footer">
                    <div style={{ borderTop: '1px solid var(--border)', paddingTop: '1rem', marginTop: '1rem' }}>
                        <div style={{ fontSize: '0.8rem', color: 'var(--muted)', marginBottom: '0.5rem' }}>Signed in as</div>
                        <div style={{ fontSize: '0.9rem', fontWeight: 600 }}>{username}</div>
                        <button className="nav-item" style={{ marginTop: '0.5rem', color: 'var(--red)' }} onClick={onLogout}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></svg>
                            Sign Out
                        </button>
                    </div>
                </div>
            </aside>

            <main className="main-content">
                {tab === 'records' && (
                    <>
                        <div className="page-header">
                            <h2>Analyst Review Dashboard</h2>
                            <p>Review ingested emission records and approve for audit.</p>
                        </div>

                        {stats && (
                            <div className="stats-grid">
                                <div className="stat-card">
                                    <div className="stat-label">Total Records</div>
                                    <div className="stat-value blue">{stats.total_records}</div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-label">Pending Review</div>
                                    <div className="stat-value yellow">{stats.pending}</div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-label">Flagged</div>
                                    <div className="stat-value red">{stats.flagged}</div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-label">Approved</div>
                                    <div className="stat-value green">{stats.approved}</div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-label">Scope 1</div>
                                    <div className="stat-value">{stats.scopes?.scope1 || 0}</div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-label">Scope 2</div>
                                    <div className="stat-value">{stats.scopes?.scope2 || 0}</div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-label">Scope 3</div>
                                    <div className="stat-value">{stats.scopes?.scope3 || 0}</div>
                                </div>
                            </div>
                        )}

                        <div className="table-card">
                            <div className="table-header">
                                <b>Emission Records</b>
                                <button className="btn-upload" style={{ width: 'auto', padding: '0.4rem 1rem' }} onClick={fetchRecords}>↻ Refresh</button>
                            </div>
                            <div className="filter-row">
                                <span style={{ color: 'var(--muted)', fontSize: '0.8rem', marginRight: '0.25rem', alignSelf: 'center' }}>Status:</span>
                                {STATUSES.map(s => (
                                    <button key={s} className={`filter-btn ${statusFilter === s ? 'active' : ''}`} onClick={() => setStatusFilter(s)}>
                                        {s.charAt(0).toUpperCase() + s.slice(1)}
                                    </button>
                                ))}
                                <span style={{ color: 'var(--muted)', fontSize: '0.8rem', marginLeft: '0.75rem', marginRight: '0.25rem', alignSelf: 'center' }}>Source:</span>
                                {SOURCES.map(s => (
                                    <button key={s} className={`filter-btn ${sourceFilter === s ? 'active' : ''}`} onClick={() => setSourceFilter(s)}>
                                        {s}
                                    </button>
                                ))}
                            </div>
                            <div className="table-wrap">
                                {loading ? (
                                    <div className="empty-state"><div className="spinner" style={{ width: 32, height: 32, margin: '2rem auto', borderWidth: 3 }} /></div>
                                ) : records.length === 0 ? (
                                    <div className="empty-state">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></svg>
                                        <p>No records found. Upload data to get started.</p>
                                    </div>
                                ) : (
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Date</th>
                                                <th>Source</th>
                                                <th>Scope</th>
                                                <th>Description</th>
                                                <th>Quantity</th>
                                                <th>CO₂ (kg)</th>
                                                <th>Status</th>
                                                <th>Reason</th>
                                                <th>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {records.map(r => (
                                                <tr key={r.id} onClick={() => setSelectedRecord(r)} style={{ cursor: 'pointer' }} title="Click to view details">
                                                    <td style={{ whiteSpace: 'nowrap' }}>{r.activity_date}</td>
                                                    <td><span className="badge pending">{r.source_type}</span></td>
                                                    <td style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>{r.scope}</td>
                                                    <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.description || '-'}</td>
                                                    <td>{r.raw_quantity} {r.raw_unit}</td>
                                                    <td>{r.co2_kg ? Number(r.co2_kg).toFixed(2) : '-'}</td>
                                                    <td><span className={`badge ${r.status}`}>{r.status}</span></td>
                                                    <td style={{ color: 'var(--red)', fontSize: '0.75rem', maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.flag_reason || '-'}</td>
                                                    <td>
                                                        {!r.is_locked && r.status !== 'approved' && (
                                                            <button className="action-btn approve" onClick={(e) => { e.stopPropagation(); handleAction(r.id, 'approve'); }}>✓ Approve</button>
                                                        )}
                                                        {!r.is_locked && r.status !== 'rejected' && (
                                                            <button className="action-btn reject" onClick={(e) => { e.stopPropagation(); handleAction(r.id, 'reject'); }}>✗ Reject</button>
                                                        )}
                                                        {r.is_locked && <span style={{ color: 'var(--muted)', fontSize: '0.75rem' }}>🔒 Locked</span>}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                )}
                            </div>
                        </div>
                    </>
                )}

                {tab === 'upload' && <UploadTab showToast={showToast} />}
                {tab === 'batches' && <BatchesTab />}
            </main>

            {selectedRecord && (
                <div className="modal-overlay" onClick={() => setSelectedRecord(null)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>Record Details</h3>
                            <button className="modal-close" onClick={() => setSelectedRecord(null)}>×</button>
                        </div>
                        <div className="modal-body">
                            <div className="detail-grid">
                                <div className="detail-item">
                                    <div className="detail-label">Source Type</div>
                                    <div className="detail-value"><span className="badge pending">{selectedRecord.source_type}</span></div>
                                </div>
                                <div className="detail-item">
                                    <div className="detail-label">Scope</div>
                                    <div className="detail-value">{selectedRecord.scope}</div>
                                </div>
                                <div className="detail-item">
                                    <div className="detail-label">Activity Date</div>
                                    <div className="detail-value">{selectedRecord.activity_date}</div>
                                </div>
                                <div className="detail-item">
                                    <div className="detail-label">Status</div>
                                    <div className="detail-value"><span className={`badge ${selectedRecord.status}`}>{selectedRecord.status}</span></div>
                                </div>
                                <div className="detail-item full-width">
                                    <div className="detail-label">Description</div>
                                    <div className="detail-value">{selectedRecord.description || '-'}</div>
                                </div>
                                <div className="detail-item">
                                    <div className="detail-label">Raw Quantity</div>
                                    <div className="detail-value">{selectedRecord.raw_quantity} {selectedRecord.raw_unit}</div>
                                </div>
                                <div className="detail-item">
                                    <div className="detail-label">Normalized Qty</div>
                                    <div className="detail-value">{selectedRecord.normalized_quantity} {selectedRecord.normalized_unit}</div>
                                </div>
                                <div className="detail-item">
                                    <div className="detail-label">CO2 Emission</div>
                                    <div className="detail-value" style={{ color: 'var(--accent)', fontWeight: 'bold' }}>
                                        {selectedRecord.co2_kg ? `${Number(selectedRecord.co2_kg).toFixed(2)} kg CO2e` : '-'}
                                    </div>
                                </div>
                                <div className="detail-item">
                                    <div className="detail-label">Amount (INR)</div>
                                    <div className="detail-value">₹ {selectedRecord.amount_inr ? Number(selectedRecord.amount_inr).toLocaleString() : '-'}</div>
                                </div>
                                <div className="detail-item">
                                    <div className="detail-label">Vendor / Reference</div>
                                    <div className="detail-value">{selectedRecord.vendor || '-'}</div>
                                </div>
                                <div className="detail-item">
                                    <div className="detail-label">Location / Site</div>
                                    <div className="detail-value">{selectedRecord.location || '-'}</div>
                                </div>
                                {selectedRecord.flag_reason && (
                                    <div className="detail-item full-width">
                                        <div className="detail-label" style={{ color: 'var(--red)' }}>Flag Reason</div>
                                        <div className="detail-value" style={{ color: 'var(--red)', background: 'rgba(239,68,68,0.1)', padding: '0.5rem', borderRadius: '0.25rem' }}>
                                            ⚠️ {selectedRecord.flag_reason}
                                        </div>
                                    </div>
                                )}
                                <div className="detail-item full-width">
                                    <div className="detail-label">Raw Data Row (CSV Export)</div>
                                    <pre className="raw-json-box">
                                        {JSON.stringify(selectedRecord.raw_row, null, 2)}
                                    </pre>
                                </div>
                            </div>
                        </div>
                        <div className="modal-footer">
                            {!selectedRecord.is_locked && selectedRecord.status !== 'approved' && (
                                <button className="action-btn approve" onClick={() => { handleAction(selectedRecord.id, 'approve'); setSelectedRecord(null); }}>✓ Approve</button>
                            )}
                            {!selectedRecord.is_locked && selectedRecord.status !== 'rejected' && (
                                <button className="action-btn reject" onClick={() => { handleAction(selectedRecord.id, 'reject'); setSelectedRecord(null); }}>✗ Reject</button>
                            )}
                            <button className="filter-btn" onClick={() => setSelectedRecord(null)}>Close</button>
                        </div>
                    </div>
                </div>
            )}
            {toast && <div className={`toast ${toast.type}`}>{toast.msg}</div>}
        </div>
    )
}

function UploadTab({ showToast }) {
    const sources = [
        { key: 'sap', label: 'SAP Export', desc: 'Fuel & Procurement (BUKRS/MATNR CSV)', endpoint: '/api/ingest/sap/' },
        { key: 'utility', label: 'Utility Bill', desc: 'Electricity portal export (kWh CSV)', endpoint: '/api/ingest/utility/' },
        { key: 'travel', label: 'Corporate Travel', desc: 'Concur/Navan CSV export', endpoint: '/api/ingest/travel/' },
    ]

    return (
        <>
            <div className="page-header">
                <h2>Upload Data</h2>
                <p>Ingest emissions data from the three supported source types.</p>
            </div>
            <div className="upload-grid">
                {sources.map(s => <UploadCard key={s.key} source={s} showToast={showToast} />)}
            </div>
        </>
    )
}

function UploadCard({ source, showToast }) {
    const [file, setFile] = useState(null)
    const [loading, setLoading] = useState(false)

    const handleUpload = async () => {
        if (!file) return
        setLoading(true)
        const formData = new FormData()
        formData.append('file', file)
        formData.append('client_slug', 'default-client')
        try {
            const r = await api.post(source.endpoint, formData)
            showToast(`✓ Ingested ${r.data.data?.rows_ingested || '?'} records from ${source.label}`)
            setFile(null)
        } catch (e) {
            showToast(`Failed to upload: ${e.response?.data?.errors?.[0] || e.message}`, 'error')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="upload-card">
            <h3>{source.label}</h3>
            <p>{source.desc}</p>
            <div className="drop-zone">
                <input type="file" accept=".csv" onChange={e => setFile(e.target.files[0])} />
                {file ? (
                    <p>📎 <strong>{file.name}</strong></p>
                ) : (
                    <p>Drop CSV here or <strong>browse</strong></p>
                )}
            </div>
            <button className="btn-upload" onClick={handleUpload} disabled={!file || loading}>
                {loading ? <><span className="spinner" style={{ marginRight: '0.5rem' }} />Uploading...</> : `Upload ${source.label}`}
            </button>
        </div>
    )
}

function BatchesTab() {
    const [batches, setBatches] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        api.get('/api/batches/').then(r => {
            setBatches(r.data.results || r.data)
            setLoading(false)
        }).catch(() => setLoading(false))
    }, [])

    return (
        <>
            <div className="page-header">
                <h2>Ingestion Batches</h2>
                <p>History of all data ingestion runs.</p>
            </div>
            <div className="table-card">
                <div className="table-wrap">
                    {loading ? (
                        <div className="empty-state"><div className="spinner" style={{ width: 32, height: 32, margin: '2rem auto', borderWidth: 3 }} /></div>
                    ) : batches.length === 0 ? (
                        <div className="empty-state"><p>No batches yet. Upload data to get started.</p></div>
                    ) : (
                        <table>
                            <thead><tr><th>ID</th><th>Source</th><th>File</th><th>Status</th><th>Rows</th><th>Errors</th><th>Uploaded</th></tr></thead>
                            <tbody>
                                {batches.map(b => (
                                    <tr key={b.id}>
                                        <td style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>{String(b.id).slice(0, 8)}</td>
                                        <td><span className="badge pending">{b.source_type}</span></td>
                                        <td>{b.file_name}</td>
                                        <td><span className={`badge ${b.status === 'done' ? 'approved' : b.status === 'failed' ? 'rejected' : 'pending'}`}>{b.status}</span></td>
                                        <td>{b.row_count}</td>
                                        <td style={{ color: b.error_count > 0 ? 'var(--red)' : 'inherit' }}>{b.error_count}</td>
                                        <td style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>{new Date(b.uploaded_at).toLocaleString()}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </>
    )
}
