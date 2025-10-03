import React, { useEffect, useState, useMemo } from 'react'
import { getJobs, createJob, deleteJob, updateJob } from './api'
import JobList from './components/JobList.jsx'
import JobForm from './components/JobForm.jsx'
import FilterBar from './components/FilterBar.jsx'

import './App.css';


export default function App() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // filters from your UI (keep 'All' in UI; we’ll strip it before calling the API)
  const [filters, setFilters] = useState({
    q: '',
    job_type: 'All',
    location: '',
    tag: '',
    sort: 'posting_date_desc'
  })

  // NEW: pagination state + meta
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [meta, setMeta] = useState({ total: 0 })

  const [editing, setEditing] = useState(null) // job being edited

  // Build API params (strip job_type=All)
  const apiParams = useMemo(() => {
    const p = { ...filters }
    if (p.job_type === 'All') delete p.job_type
    p.page = page
    p.page_size = pageSize
    return p
  }, [filters, page, pageSize])

  const fetchJobs = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getJobs(apiParams)
      setJobs(data.jobs || [])
      setMeta({ total: data.total || 0 })
    } catch (err) {
      setError(err?.message || 'Failed to fetch jobs')
    } finally {
      setLoading(false)
    }
  }

  // Fetch whenever params change
  useEffect(() => { fetchJobs() }, [apiParams]) // eslint-disable-line react-hooks/exhaustive-deps

  // Whenever filters change, reset to the first page
  useEffect(() => { setPage(1) }, [filters])

  const handleAdd = async (payload) => {
    setLoading(true)
    setError(null)
    try {
      const { job } = await createJob(payload)
      // Prepend new job; optionally refetch to keep counts correct
      setJobs(prev => [job, ...prev])
      // If you want the total to be exact, you could refetch:
      // await fetchJobs()
      alert('Job added successfully.')
    } catch (err) {
      alert('Failed to add job: ' + (err?.response?.data?.error || err.message))
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this job?')) return
    setLoading(true)
    try {
      await deleteJob(id)
      setJobs(prev => prev.filter(j => j.id !== id))
      // Optionally refetch to keep pagination totals consistent:
      // await fetchJobs()
      alert('Job deleted.')
    } catch (err) {
      alert('Delete failed: ' + (err?.response?.data?.error || err.message))
    } finally {
      setLoading(false)
    }
  }

  const handleStartEdit = (job) => setEditing(job)

  const handleSaveEdit = async (id, updates) => {
    setLoading(true)
    try {
      const { job } = await updateJob(id, updates)
      setJobs(prev => prev.map(j => (j.id === id ? job : j)))
      setEditing(null)
      alert('Job updated.')
    } catch (err) {
      alert('Update failed: ' + (err?.response?.data?.error || err.message))
    } finally {
      setLoading(false)
    }
  }

  // Helper to compute page count and boundaries
  const totalPages = Math.max(1, Math.ceil((meta.total || 0) / pageSize))
  const canPrev = page > 1
  const canNext = page < totalPages

  return (
    <div className="container">
      <header>
        <h1>Actuarial Job Board</h1>
        <p className="muted">Browse, add, edit, and filter actuarial jobs.</p>
      </header>

      <FilterBar value={filters} onChange={setFilters} />

      <section className="grid">
        <div>
          <h2>Add / Edit Job</h2>
          <JobForm
            key={editing ? editing.id : 'new'}
            initial={editing}
            onSubmit={editing ? (payload) => handleSaveEdit(editing.id, payload) : handleAdd}
            onCancel={() => setEditing(null)}
          />
        </div>

        <div>
          <h2>Jobs</h2>
          {loading && <div className="notice">Loading…</div>}
          {error && <div className="error">{error}</div>}

          <JobList jobs={jobs} onDelete={handleDelete} onEdit={handleStartEdit} />

          {/* Pagination controls */}
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 12 }}>
            <button disabled={!canPrev} onClick={() => setPage(p => Math.max(1, p - 1))}>
              Prev
            </button>
            <span className="muted small">
              Page {page} of {totalPages} &nbsp;|&nbsp; Total {meta.total || 0}
            </span>
            <button disabled={!canNext} onClick={() => setPage(p => Math.min(totalPages, p + 1))}>
              Next
            </button>

            <label className="muted small" style={{ marginLeft: 'auto' }}>
              Page size:&nbsp;
              <select
                value={pageSize}
                onChange={e => { setPage(1); setPageSize(parseInt(e.target.value, 10)) }}
              >
                <option value="10">10</option>
                <option value="20">20</option>
                <option value="30">30</option>
                <option value="50">50</option>
              </select>
            </label>
          </div>
        </div>
      </section>
    </div>
  )
}
