import { useState, useEffect } from 'react'
import { TrendingUp, Send, Mic, XCircle } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Dashboard({ stats, onRefresh }) {
  const [recentJobs, setRecentJobs] = useState([])

  useEffect(() => {
    fetchJobs()
  }, [])

  const fetchJobs = async () => {
    try {
      const res = await fetch(`${API_URL}/api/jobs?status=found`)
      const data = await res.json()
      setRecentJobs(data.slice(0, 5))
    } catch (e) {
      console.error('Failed to fetch jobs:', e)
    }
  }

  const statCards = [
    { label: 'Found', value: stats.found, color: 'bg-blue-500', icon: TrendingUp },
    { label: 'Applied', value: stats.applied, color: 'bg-green-500', icon: Send },
    { label: 'Interview', value: stats.interview, color: 'bg-purple-500', icon: Mic },
    { label: 'Rejected', value: stats.rejected, color: 'bg-red-500', icon: XCircle },
  ]

  const statusEmoji = {
    found: '🆕',
    applied: '📤',
    interview: '🎤',
    rejected: '❌',
    offer: '🎉'
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Dashboard</h2>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {statCards.map(card => (
          <div key={card.label} className="card">
            <div className="flex items-center gap-3">
              <div className={`${card.color} p-3 rounded-lg text-white`}>
                <card.icon size={24} />
              </div>
              <div>
                <p className="text-2xl font-bold">{card.value}</p>
                <p className="text-sm text-gray-500">{card.label}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Jobs */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Recent Jobs</h3>
        {recentJobs.length === 0 ? (
          <p className="text-gray-500">No jobs found yet. Run a scan to populate.</p>
        ) : (
          <div className="space-y-3">
            {recentJobs.map(job => (
              <div key={job.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-3 bg-gray-50 rounded-lg gap-2">
                <div className="flex items-center gap-3">
                  <span className="text-xl">{statusEmoji[job.status] || '📋'}</span>
                  <div className="min-w-0">
                    <p className="font-medium truncate">{job.title}</p>
                    <p className="text-sm text-gray-500">{job.company}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 sm:text-right">
                  <span className="inline-block px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm font-medium">
                    Score: {job.score}
                  </span>
                  {job.has_early_applicant && (
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                      Early
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
