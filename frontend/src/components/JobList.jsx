import React from 'react'
import JobCard from './JobCard.jsx'

export default function JobList({ jobs, onDelete, onEdit }) {
  if (!jobs.length) return <div className="notice">No jobs found.</div>
  return (
    <div className="list">
      {jobs.map(j => <JobCard key={j.id} job={j} onDelete={onDelete} onEdit={onEdit} />)}
    </div>
  )
}
