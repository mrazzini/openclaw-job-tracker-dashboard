import { useState, useEffect } from 'react'
import { LayoutDashboard, Briefcase, Code, FileText, Menu, X } from 'lucide-react'
import Dashboard from './components/Dashboard'
import Jobs from './components/Jobs'
import Skills from './components/Skills'
import CVs from './components/CVs'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [page, setPage] = useState('dashboard')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
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
    <div className="min-h-screen flex flex-col md:flex-row">
      {/* Mobile Header */}
      <header className="md:hidden bg-white border-b border-gray-200 p-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-primary flex items-center gap-2">
          🦅 Ambros
        </h1>
        <button 
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-2 text-gray-600"
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </header>

      {/* Sidebar - Desktop + Mobile overlay */}
      <aside className={`${mobileMenuOpen ? 'block' : 'hidden'} md:block md:w-64 bg-white border-r border-gray-200 flex-shrink-0 fixed md:relative inset-0 z-50 md:z-auto`}>
        <div className="hidden md:block p-6">
          <h1 className="text-2xl font-bold text-primary flex items-center gap-2">
            🦅 Ambros
          </h1>
          <p className="text-sm text-gray-500 mt-1">Job Tracker</p>
        </div>
        <nav className="px-4 pt-4 md:pt-0">
          {navItems.map(item => (
            <button
              key={item.id}
              onClick={() => { setPage(item.id); setMobileMenuOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-1 transition-colors ${
                page === item.id
                  ? 'bg-blue-50 text-blue-600 font-medium'
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
      <main className="flex-1 p-4 md:p-8 overflow-x-hidden">
        {page === 'dashboard' && <Dashboard stats={stats} onRefresh={fetchStats} />}
        {page === 'jobs' && <Jobs apiUrl={API_URL} />}
        {page === 'skills' && <Skills apiUrl={API_URL} />}
        {page === 'cvs' && <CVs apiUrl={API_URL} />}
      </main>
    </div>
  )
}

export default App
