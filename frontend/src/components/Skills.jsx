import { useState, useEffect } from 'react'
import { Plus, Trash2 } from 'lucide-react'

export default function Skills({ apiUrl }) {
  const [skills, setSkills] = useState([])
  const [showAdd, setShowAdd] = useState(false)
  const [newSkill, setNewSkill] = useState({ name: '', level: 'Strong', category: 'Languages' })

  useEffect(() => {
    fetchSkills()
  }, [])

  const fetchSkills = async () => {
    try {
      const res = await fetch(`${apiUrl}/api/skills`)
      const data = await res.json()
      setSkills(data)
    } catch (e) {
      console.error('Failed to fetch skills:', e)
    }
  }

  const addSkill = async () => {
    if (!newSkill.name.trim()) return
    try {
      await fetch(`${apiUrl}/api/skills`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSkill)
      })
      setNewSkill({ name: '', level: 'Strong', category: 'Languages' })
      setShowAdd(false)
      fetchSkills()
    } catch (e) {
      console.error('Failed to add skill:', e)
    }
  }

  const deleteSkill = async (id) => {
    try {
      await fetch(`${apiUrl}/api/skills/${id}`, { method: 'DELETE' })
      fetchSkills()
    } catch (e) {
      console.error('Failed to delete skill:', e)
    }
  }

  const categories = ['Languages', 'ML/AI', 'Data', 'DevOps', 'Tools', 'Other']
  const levels = ['Expert', 'Strong', 'Working', 'Learning', 'None']

  const skillsByCategory = categories.reduce((acc, cat) => {
    acc[cat] = skills.filter(s => s.category === cat)
    return acc
  }, {})

  const levelColors = {
    Expert: 'bg-purple-100 text-purple-700',
    Strong: 'bg-green-100 text-green-700',
    Working: 'bg-blue-100 text-blue-700',
    Learning: 'bg-yellow-100 text-yellow-700',
    None: 'bg-gray-100 text-gray-500'
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Skills Matrix</h2>
        <button onClick={() => setShowAdd(!showAdd)} className="btn btn-primary flex items-center gap-2">
          <Plus size={18} /> Add Skill
        </button>
      </div>

      {/* Add Skill Form */}
      {showAdd && (
        <div className="card mb-6">
          <h3 className="font-semibold mb-4">Add New Skill</h3>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <input
              type="text"
              placeholder="Skill name"
              value={newSkill.name}
              onChange={e => setNewSkill({ ...newSkill, name: e.target.value })}
              className="border rounded-lg px-3 py-2"
            />
            <select
              value={newSkill.level}
              onChange={e => setNewSkill({ ...newSkill, level: e.target.value })}
              className="border rounded-lg px-3 py-2"
            >
              {levels.map(l => <option key={l} value={l}>{l}</option>)}
            </select>
            <select
              value={newSkill.category}
              onChange={e => setNewSkill({ ...newSkill, category: e.target.value })}
              className="border rounded-lg px-3 py-2"
            >
              {categories.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <button onClick={addSkill} className="btn btn-primary">Save Skill</button>
        </div>
      )}

      {/* Skills by Category */}
      {categories.map(cat => (
        skillsByCategory[cat]?.length > 0 && (
          <div key={cat} className="card mb-4">
            <h3 className="font-semibold text-lg mb-3">{cat}</h3>
            <div className="flex flex-wrap gap-2">
              {skillsByCategory[cat].map(skill => (
                <div
                  key={skill.id}
                  className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg group"
                >
                  <span className="font-medium">{skill.name}</span>
                  <span className={`px-2 py-0.5 rounded text-xs ${levelColors[skill.level]}`}>
                    {skill.level}
                  </span>
                  <button
                    onClick={() => deleteSkill(skill.id)}
                    className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )
      ))}

      {skills.length === 0 && (
        <p className="text-center text-gray-500 py-8">No skills added yet</p>
      )}
    </div>
  )
}
