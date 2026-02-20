import { useState, useEffect } from 'react'
import { ExternalLink, Check, X, Plus } from 'lucide-react'

export default function Jobs({ apiUrl }) {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('All')
  const [showAdd, setShowAdd] = useState(false)
  const [newJob, setNewJob] = useState({ title: '', company: '', url: '', score: 60, requirements: '' })

  useEffect(() => {
    fetchJobs()
  }, [filter])

  const fetchJobs = async () => {
    setLoading(true)
    try {
      const url = filter === 'All' ? `${apiUrl}/api/jobs` : `${apiUrl}/api/jobs?status=${filter}`
      const res = await fetch(url)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setJobs(data)
    } catch (e) {
      console.error('Failed to fetch jobs:', e)
    } finally {
      setLoading(false)
    }
  }

  const updateStatus = async (jobId, status) => {
    try {
      await fetch(`${apiUrl}/api/jobs/${jobId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      })
      fetchJobs()
    } catch (e) {
      console.error('Failed to update job:', e)
    }
  }

  const addJob = async () => {
    try {
      await fetch(`${apiUrl}/api/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...newJob, has_early_applicant: false })
      })
      setShowAdd(false)
      setNewJob({ title: '', company: '', url: '', score: 60, requirements: '' })
      fetchJobs()
    } catch (e) {
      console.error('Failed to add job:', e)
    }
  }

  const statusOptions = ['found', 'applied', 'interview', 'rejected', 'offer']
  const statusColors = {
    found: 'bg-blue-100 text-blue-700',
    applied: 'bg-green-100 text-green-700',
    interview: 'bg-purple-100 text-purple-700',
    rejected: 'bg-red-100 text-red-700',
    offer: 'bg-yellow-100 text-yellow-700'
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Jobs</h2>
        <button onClick={() => setShowAdd(!showAdd)} className="btn btn-primary flex items-center gap-2">
          <Plus size={18} /> Add Job
        </button>
      </div>

      {/* Add Job Form */}
      {showAdd && (
        <div className="card mb-6">
          <h3 className="font-semibold mb-4">Add New Job</h3>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <input
              type="text" placeholder="Job Title"
              value={newJob.title}
              onChange={e => setNewJob({ ...newJob, title: e.target.value })}
              className="border rounded-lg px-3 py-2"
            />
            <input
              type="text" placeholder="Company"
              value={newJob.company}
              onChange={e => setNewJob({ ...newJob, company: e.target.value })}
              className="border rounded-lg px-3 py-2"
            />
            <input
              type="text" placeholder="LinkedIn URL"
              value={newJob.url}
              onChange={e => setNewJob({ ...newJob, url: e.target.value })}
              className="border rounded-lg px-3 py-2 col-span-2"
            />
            <input
              type="number" placeholder="Score"
              value={newJob.score}
              onChange={e => setNewJob({ ...newJob, score: parseInt(e.target.value) })}
              className="border rounded-lg px-3 py-2"
            />
            <input
              type="text" placeholder="Requirements"
              value={newJob.requirements}
              onChange={e => setNewJob({ ...newJob, requirements: e.target.value })}
              className="border rounded-lg px-3 py-2"
            />
          </div>
          <button onClick={addJob} className="btn btn-primary">Save Job</button>
        </div>
      )}

      {/* Filter */}
      <div className="flex gap-2 mb-6 overflow-x-auto">
        {['All', ...statusOptions].map(status => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap ${
              filter === status ? 'bg-primary text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </button>
        ))}
      </div>

      {/* Jobs List */}
      <div className="space-y-4">
        {jobs.map(job => (
          <div key={job.id} className="card">
            <div className="flex justify-between items-start mb-3">
              <div>
                <h3 className="font-semibold text-lg">{job.title}</h3>
                <p className="text-gray-500">{job.company}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                  Score: {job.score}
                </span>
                {job.has_early_applicant && (
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">Early</span>
                )}
              </div>
            </div>
            
            {job.requirements && (
              <p className="text-sm text-gray-600 mb-3">{job.requirements}</p>
            )}
            
            <div className="flex items-center justify-between">
              <div className="flex gap-2">
                <a href={job.url} target="_blank" rel="noopener noreferrer" 
                   className="btn btn-secondary flex items-center gap-1 text-sm">
                  <ExternalLink size={14} /> View
                </a>
                
                <select
                  value={job.status}
                  onChange={e => updateStatus(job.id, e.target.value)}
                  className={`px-3 py-1 rounded text-sm ${statusColors[job.status]}`}
                >
                  {statusOptions.map(s => (
                    <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
                  ))}
                </select>
              </div>
              
              <p className="text-xs text-gray-400">
                Found: {new Date(job.found_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        ))}
        
        {loading && (
          <p className="text-center text-gray-500 py-8">Loading jobs...</p>
        )}
        {!loading && jobs.length === 0 && (
          <p className="text-center text-gray-500 py-8">No jobs found for filter: {filter}</p>
        )}
      </div>
    </div>
  )
}
