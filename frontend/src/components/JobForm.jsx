import React, { useState, useEffect } from 'react'

export default function JobForm({ initial, onSubmit, onCancel }) {
  const [title, setTitle] = useState('')
  const [company, setCompany] = useState('')
  const [location, setLocation] = useState('')
  const [posting_date, setPostingDate] = useState('')
  const [job_type, setJobType] = useState('Full-time')
  const [tagsText, setTagsText] = useState('')
  const [source_url, setSourceUrl] = useState('')
  const [errors, setErrors] = useState({})

  useEffect(() => {
    setTitle(initial?.title || '')
    setCompany(initial?.company || '')
    setLocation(initial?.location || '')
    setPostingDate(initial?.posting_date || '')
    setJobType(initial?.job_type || 'Full-time')
    setTagsText((initial?.tags || []).join(', '))
    setSourceUrl(initial?.source_url || '')
  }, [initial])

  const validate = () => {
    const errs = {}
    if (!title.trim()) errs.title = 'Title is required'
    if (!company.trim()) errs.company = 'Company is required'
    if (!location.trim()) errs.location = 'Location is required'
    if (posting_date && !/^\d{4}-\d{2}-\d{2}$/.test(posting_date)) {
      errs.posting_date = 'Use YYYY-MM-DD'
    }
    if (source_url && !/^https?:\/\//i.test(source_url)) {
      errs.source_url = 'Must start with http(s)://'
    }
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const submit = (e) => {
    e.preventDefault()
    if (!validate()) return
    const tags = tagsText.split(',').map(t => t.trim()).filter(Boolean)
    onSubmit({ title, company, location, posting_date, job_type, tags, source_url })
  }

  return (
    <form className="form card" onSubmit={submit} noValidate>
      <div className="form-grid">
        <label>Title
          <input value={title} onChange={e => setTitle(e.target.value)} />
          {errors.title && <span className="error">{errors.title}</span>}
        </label>

        <label>Company
          <input value={company} onChange={e => setCompany(e.target.value)} />
          {errors.company && <span className="error">{errors.company}</span>}
        </label>

        <label>Location
          <input value={location} onChange={e => setLocation(e.target.value)} />
          {errors.location && <span className="error">{errors.location}</span>}
        </label>

        <label>Posting Date (YYYY-MM-DD)
          <input value={posting_date} onChange={e => setPostingDate(e.target.value)} placeholder="e.g., 2025-10-02" />
          {errors.posting_date && <span className="error">{errors.posting_date}</span>}
        </label>

        <label>Job Type
          <select value={job_type} onChange={e => setJobType(e.target.value)}>
            <option>Full-time</option>
            <option>Part-time</option>
            <option>Contract</option>
            <option>Internship</option>
          </select>
        </label>

        <label>Source URL
          <input value={source_url} onChange={e => setSourceUrl(e.target.value)} placeholder="https://…" />
          {errors.source_url && <span className="error">{errors.source_url}</span>}
        </label>

        <label className="span-2">Tags (comma separated)
          <input value={tagsText} onChange={e => setTagsText(e.target.value)} placeholder="Life, Health, Pricing" />
        </label>
      </div>

      <div className="actions">
        <button type="submit" className="btn primary">{initial ? 'Save Changes' : 'Add Job'}</button>
        {initial && <button type="button" className="btn ghost" onClick={onCancel}>Cancel</button>}
      </div>
    </form>
  )
}
