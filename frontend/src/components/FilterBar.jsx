import React, { useState, useEffect } from 'react'

export default function FilterBar({ value, onChange }) {
  const [q, setQ] = useState(value.q || '')
  const [jobType, setJobType] = useState(value.job_type || 'All')
  const [location, setLocation] = useState(value.location || '')
  const [tag, setTag] = useState(value.tag || '')
  const [sort, setSort] = useState(value.sort || 'posting_date_desc')

  // keep local inputs in sync if parent resets filters
  useEffect(() => {
    setQ(value.q || '')
    setJobType(value.job_type || 'All')
    setLocation(value.location || '')
    setTag(value.tag || '')
    setSort(value.sort || 'posting_date_desc')
  }, [value])

  const apply = (e) => {
    if (e) e.preventDefault()
    onChange({ q, job_type: jobType, location, tag, sort })
  }

  const reset = () => {
    setQ(''); setJobType('All'); setLocation(''); setTag(''); setSort('posting_date_desc')
    onChange({ q: '', job_type: 'All', location: '', tag: '', sort: 'posting_date_desc' })
  }

  return (
    <form className="toolbar sticky" onSubmit={apply}>
      <div className="toolbar-row">
        <div className="field">
          <input
            value={q}
            onChange={e => setQ(e.target.value)}
            placeholder="Search title, company, tags…"
            aria-label="Search"
          />
        </div>

        <div className="field">
          <select value={jobType} onChange={e => setJobType(e.target.value)} aria-label="Job type">
            <option>All</option>
            <option>Full-time</option>
            <option>Part-time</option>
            <option>Remote</option>
            <option>Internship</option>
          </select>
        </div>

        <div className="field">
          <input
            value={location}
            onChange={e => setLocation(e.target.value)}
            placeholder="Location (e.g., London)"
            aria-label="Location"
          />
        </div>

        <div className="field">
          <input
            value={tag}
            onChange={e => setTag(e.target.value)}
            placeholder="Tag (e.g., Pricing)"
            aria-label="Tag"
          />
        </div>

        <div className="field">
          <select value={sort} onChange={e => setSort(e.target.value)} aria-label="Sort">
            <optgroup label="Date">
              <option value="posting_date_desc">Newest first</option>
              <option value="posting_date_asc">Oldest first</option>
            </optgroup>
            <optgroup label="Alphabetical">
              <option value="title_asc">Title A→Z</option>
              <option value="company_asc">Company A→Z</option>
            </optgroup>
          </select>
        </div>

        <div className="actions">
          <button type="submit" className="btn primary">Apply</button>
          <button type="button" className="btn ghost" onClick={reset}>Reset</button>
        </div>
      </div>
    </form>
  )
}
