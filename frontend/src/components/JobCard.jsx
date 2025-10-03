import React from 'react'

function initials(text = '') {
  const parts = text.split(' ').filter(Boolean)
  const a = (parts[0] || '')[0] || ''
  const b = (parts[1] || '')[0] || ''
  return (a + b).toUpperCase()
}

export default function JobCard({ job, onDelete, onEdit }) {
  return (
    <article className="card job-card">
      <header className="card-head">
        <div className="avatar">{initials(job.company || 'A')}</div>
        <div className="titleblock">
          <h3 className="title">{job.title}</h3>
          <p className="muted">{job.company} • {job.location}</p>
        </div>
        <span className="badge">{job.job_type || 'N/A'}</span>
      </header>

      {job.posting_date && (
        <p className="muted small">Posted: {job.posting_date}</p>
      )}

      {!!(job.tags && job.tags.length) && (
        <div className="tags">
          {job.tags.map((t, i) => <span key={i} className="chip">{t}</span>)}
        </div>
      )}

      <footer className="actions wrap">
        <button onClick={() => onEdit(job)} className="btn">Edit</button>
        {job.source_url && (
          <a href={job.source_url} target="_blank" rel="noreferrer" className="btn ghost">
            View Job
          </a>
        )}
        <button className="btn danger" onClick={() => onDelete(job.id)}>Delete</button>
      </footer>
    </article>
  )
}
