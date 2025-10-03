import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000/api'

export async function getJobs(params = {}) {
  const { data } = await axios.get(`${BASE}/jobs`, { params })
  return data
}

export async function createJob(payload) {
  const { data } = await axios.post(`${BASE}/jobs`, payload)
  return data
}

export async function updateJob(id, updates) {
  const { data } = await axios.put(`${BASE}/jobs/${id}`, updates)
  return data
}

export async function deleteJob(id) {
  const { data } = await axios.delete(`${BASE}/jobs/${id}`)
  return data
}
