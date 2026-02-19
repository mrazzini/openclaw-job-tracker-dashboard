import { useState, useEffect } from 'react'
import { Plus, Trash2, Download, Upload } from 'lucide-react'

export default function CVs({ apiUrl }) {
  const [cvs, setCvs] = useState([])
  const [showAdd, setShowAdd] = useState(false)
  const [newCv, setNewCv] = useState({ name: '', version: '', content: '' })

  useEffect(() => {
    fetchCvs()
  }, [])

  const fetchCvs = async () => {
    try {
      const res = await fetch(`${apiUrl}/api/cvs`)
      const data = await res.json()
      setCvs(data)
    } catch (e) {
      console.error('Failed to fetch CVs:', e)
    }
  }

  const addCv = async () => {
    if (!newCv.name.trim()) return
    try {
      await fetch(`${apiUrl}/api/cvs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newCv)
      })
      setNewCv({ name: '', version: '', content: '' })
      setShowAdd(false)
      fetchCvs()
    } catch (e) {
      console.error('Failed to add CV:', e)
    }
  }

  const deleteCv = async (id) => {
    try {
      await fetch(`${apiUrl}/api/cvs/${id}`, { method: 'DELETE' })
      fetchCvs()
    } catch (e) {
      console.error('Failed to delete CV:', e)
    }
  }

  const exportData = async () => {
    try {
      const res = await fetch(`${apiUrl}/api/export`)
      const data = await res.json()
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `ambros-backup-${new Date().toISOString().split('T')[0]}.json`
      a.click()
    } catch (e) {
      console.error('Failed to export:', e)
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">CV Vault</h2>
        <div className="flex gap-2">
          <button onClick={exportData} className="btn btn-secondary flex items-center gap-2">
            <Download size={18} /> Export
          </button>
          <button onClick={() => setShowAdd(!showAdd)} className="btn btn-primary flex items-center gap-2">
            <Plus size={18} /> Add CV
          </button>
        </div>
      </div>

      {/* Add CV Form */}
      {showAdd && (
        <div className="card mb-6">
          <h3 className="font-semibold mb-4">Add New CV</h3>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <input
              type="text"
              placeholder="CV Name (e.g., General ML Engineer)"
              value={newCv.name}
              onChange={e => setNewCv({ ...newCv, name: e.target.value })}
              className="border rounded-lg px-3 py-2"
            />
            <input
              type="text"
              placeholder="Version (e.g., v1.0)"
              value={newCv.version}
              onChange={e => setNewCv({ ...newCv, version: e.target.value })}
              className="border rounded-lg px-3 py-2"
            />
          </div>
          <textarea
            placeholder="Paste CV content or notes..."
            value={newCv.content}
            onChange={e => setNewCv({ ...newCv, content: e.target.value })}
            className="border rounded-lg px-3 py-2 w-full h-40 mb-4"
          />
          <button onClick={addCv} className="btn btn-primary">Save CV</button>
        </div>
      )}

      {/* CVs List */}
      <div className="grid gap-4 md:grid-cols-2">
        {cvs.map(cv => (
          <div key={cv.id} className="card">
            <div className="flex justify-between items-start mb-2">
              <div>
                <h3 className="font-semibold">{cv.name}</h3>
                <p className="text-sm text-gray-500">Version: {cv.version}</p>
              </div>
              <button
                onClick={() => deleteCv(cv.id)}
                className="text-red-500 hover:text-red-700"
              >
                <Trash2 size={18} />
              </button>
            </div>
            <p className="text-sm text-gray-600 whitespace-pre-wrap line-clamp-4">
              {cv.content || 'No content'}
            </p>
            <p className="text-xs text-gray-400 mt-3">
              Updated: {new Date(cv.updated_at).toLocaleDateString()}
            </p>
          </div>
        ))}
      </div>

      {cvs.length === 0 && (
        <p className="text-center text-gray-500 py-8">No CVs added yet</p>
      )}
    </div>
  )
}
