import { useState, useEffect } from 'react'
import { LayoutDashboard, Briefcase, Code, FileText, Settings } from 'lucide-react'
import Dashboard from './components/Dashboard'
import Jobs from './components/Jobs'
import Skills from './components/Skills'
import CVs from './components/CVs'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [page, setPage] = useState('dashboard')
  const [stats, setStats] = useState({ found: 0, applied: 0, interview: 0, rejected: 0 })

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_URL}/api/stats`)
      const data = await res.json()
      setStats(data)
    } catch (e) {
      console.error('Failed to fetch stats:', e)
    }
  }

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'jobs', label: 'Jobs', icon: Briefcase },
    { id: 'skills', label: 'Skills', icon: Code },
    { id: 'cvs', label: 'CVs', icon: FileText },
  ]

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex-shrink-0">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-primary flex items-center gap-2">
            🦅 Ambros
          </h1>
          <p className="text-sm text-gray-500 mt-1">Job Tracker</p>
        </div>
        <nav className="px-4">
          {navItems.map(item => (
            <button
              key={item.id}
              onClick={() => setPage(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-1 transition-colors ${
                page === item.id
                  ? 'bg-blue-50 text-primary font-medium'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <item.icon size={20} />
              {item.label}
            </button>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-8">
        {page === 'dashboard' && <Dashboard stats={stats} onRefresh={fetchStats} />}
        {page === 'jobs' && <Jobs apiUrl={API_URL} />}
        {page === 'skills' && <Skills apiUrl={API_URL} />}
        {page === 'cvs' && <CVs apiUrl={API_URL} />}
      </main>
    </div>
  )
}

export default App
