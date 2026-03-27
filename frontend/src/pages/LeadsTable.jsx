import { useState, useEffect, useCallback } from 'react'
import { getLeads, getFilterOptions, updateLead, deleteLead } from '../lib/api'
import {
  Search, Filter, ChevronLeft, ChevronRight, ExternalLink, Trash2, Edit3, X, Check,
  ArrowUpDown,
} from 'lucide-react'

const PRIORITY_STYLES = {
  'A+': 'bg-red-500/20 text-red-300 border-red-500/30',
  A: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  B: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  C: 'bg-gray-500/20 text-gray-300 border-gray-500/30',
}

const STATUS_STYLES = {
  new: 'bg-blue-500/20 text-blue-300',
  researching: 'bg-purple-500/20 text-purple-300',
  qualified: 'bg-indigo-500/20 text-indigo-300',
  contacted: 'bg-amber-500/20 text-amber-300',
  replied: 'bg-emerald-500/20 text-emerald-300',
  meeting: 'bg-teal-500/20 text-teal-300',
  proposal: 'bg-cyan-500/20 text-cyan-300',
  won: 'bg-green-500/20 text-green-300',
  lost: 'bg-red-500/20 text-red-300',
  archived: 'bg-gray-500/20 text-gray-300',
}

function LeadDetailPanel({ lead, options, onUpdate, onClose }) {
  const [editing, setEditing] = useState({})

  const handleSave = async (field, value) => {
    await onUpdate(lead.id, { [field]: value })
    setEditing((prev) => ({ ...prev, [field]: false }))
  }

  const fields = [
    { key: 'company', label: 'Company' },
    { key: 'job_title', label: 'Job Title' },
    { key: 'country', label: 'Country' },
    { key: 'city', label: 'City' },
    { key: 'demand_signal', label: 'Demand Signal' },
    { key: 'service_needed', label: 'Service Needed' },
    { key: 'website', label: 'Website', link: true },
    { key: 'decision_maker_name', label: 'Decision Maker' },
    { key: 'decision_maker_title', label: 'DM Title' },
    { key: 'decision_maker_email', label: 'DM Email' },
    { key: 'decision_maker_linkedin', label: 'DM LinkedIn', link: true },
    { key: 'budget', label: 'Budget' },
    { key: 'skills', label: 'Skills' },
    { key: 'notes', label: 'Notes' },
  ]

  return (
    <div className="fixed inset-y-0 right-0 w-[420px] bg-gray-900 border-l border-gray-800 z-50 overflow-y-auto shadow-2xl">
      <div className="sticky top-0 bg-gray-900 border-b border-gray-800 p-4 flex items-center justify-between">
        <h2 className="font-bold text-lg truncate">{lead.company}</h2>
        <button onClick={onClose} className="text-gray-400 hover:text-white">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="p-4 space-y-4">
        {/* Status & Priority */}
        <div className="flex gap-3">
          <div className="flex-1">
            <label className="text-xs text-gray-500 block mb-1">Status</label>
            <select
              value={lead.status}
              onChange={(e) => onUpdate(lead.id, { status: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm"
            >
              {(options.statuses || []).map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <div className="flex-1">
            <label className="text-xs text-gray-500 block mb-1">Priority</label>
            <select
              value={lead.priority}
              onChange={(e) => onUpdate(lead.id, { priority: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm"
            >
              {(options.priorities || []).map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Job URL */}
        {lead.job_url && (
          <a
            href={lead.job_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-indigo-400 hover:text-indigo-300"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            View original posting
          </a>
        )}

        {/* Detail fields */}
        <div className="space-y-3">
          {fields.map(({ key, label, link }) => {
            const value = lead[key] || ''
            if (!value) return null
            return (
              <div key={key}>
                <label className="text-xs text-gray-500">{label}</label>
                {link && value.startsWith('http') ? (
                  <a
                    href={value}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-sm text-indigo-400 hover:text-indigo-300 truncate"
                  >
                    {value}
                  </a>
                ) : (
                  <p className="text-sm text-gray-200 break-words">{value}</p>
                )}
              </div>
            )
          })}
        </div>

        {/* Meta */}
        <div className="pt-3 border-t border-gray-800 text-xs text-gray-500 space-y-1">
          <p>Source: {lead.source_name}</p>
          <p>Type: {lead.lead_type}</p>
          <p>Created: {new Date(lead.created_at).toLocaleDateString()}</p>
        </div>
      </div>
    </div>
  )
}

export default function LeadsTable() {
  const [data, setData] = useState({ leads: [], total: 0, page: 1, per_page: 50, total_pages: 0 })
  const [options, setOptions] = useState({})
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    search: '', source: '', priority: '', status: '', country: '',
    sort_by: 'created_at', sort_dir: 'desc', page: 1, per_page: 50,
  })
  const [selected, setSelected] = useState(null)
  const [showFilters, setShowFilters] = useState(false)

  const loadLeads = useCallback(async () => {
    setLoading(true)
    try {
      const result = await getLeads(filters)
      setData(result)
    } catch (err) {
      console.error('Failed to load leads:', err)
    }
    setLoading(false)
  }, [filters])

  useEffect(() => {
    loadLeads()
  }, [loadLeads])

  useEffect(() => {
    getFilterOptions().then(setOptions).catch(console.error)
  }, [])

  const handleUpdate = async (id, updates) => {
    try {
      const updated = await updateLead(id, updates)
      setData((prev) => ({
        ...prev,
        leads: prev.leads.map((l) => (l.id === id ? { ...l, ...updated } : l)),
      }))
      if (selected?.id === id) setSelected((prev) => ({ ...prev, ...updated }))
    } catch (err) {
      alert(`Update failed: ${err.message}`)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this lead?')) return
    try {
      await deleteLead(id)
      setData((prev) => ({
        ...prev,
        leads: prev.leads.filter((l) => l.id !== id),
        total: prev.total - 1,
      }))
      if (selected?.id === id) setSelected(null)
    } catch (err) {
      alert(`Delete failed: ${err.message}`)
    }
  }

  const setFilter = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }))
  }

  const toggleSort = (col) => {
    setFilters((prev) => ({
      ...prev,
      sort_by: col,
      sort_dir: prev.sort_by === col && prev.sort_dir === 'desc' ? 'asc' : 'desc',
    }))
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Leads</h1>
          <p className="text-sm text-gray-500">{data.total} total leads</p>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="flex gap-3 items-center">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            value={filters.search}
            onChange={(e) => setFilter('search', e.target.value)}
            placeholder="Search companies, titles, signals..."
            className="w-full pl-10 pr-4 py-2.5 bg-gray-900 border border-gray-800 rounded-xl text-sm focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`px-4 py-2.5 rounded-xl border text-sm flex items-center gap-2 transition-colors ${
            showFilters ? 'bg-indigo-500/20 border-indigo-500/50 text-indigo-300' : 'bg-gray-900 border-gray-800 text-gray-400 hover:text-gray-200'
          }`}
        >
          <Filter className="w-4 h-4" />
          Filters
        </button>
      </div>

      {/* Filter Row */}
      {showFilters && (
        <div className="flex flex-wrap gap-3 p-4 bg-gray-900 border border-gray-800 rounded-xl">
          <select
            value={filters.source}
            onChange={(e) => setFilter('source', e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">All Sources</option>
            {(options.sources || []).map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <select
            value={filters.priority}
            onChange={(e) => setFilter('priority', e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">All Priorities</option>
            {(options.priorities || []).map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
          <select
            value={filters.status}
            onChange={(e) => setFilter('status', e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">All Statuses</option>
            {(options.statuses || []).map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <select
            value={filters.country}
            onChange={(e) => setFilter('country', e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">All Countries</option>
            {(options.countries || []).map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          {Object.values(filters).some((v) => v && v !== 'created_at' && v !== 'desc' && v !== 1 && v !== 50) && (
            <button
              onClick={() =>
                setFilters({ search: '', source: '', priority: '', status: '', country: '', sort_by: 'created_at', sort_dir: 'desc', page: 1, per_page: 50 })
              }
              className="text-xs text-red-400 hover:text-red-300 px-3 py-2"
            >
              Clear all
            </button>
          )}
        </div>
      )}

      {/* Table */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-gray-400">
                {[
                  { key: 'company', label: 'Company' },
                  { key: 'source_name', label: 'Source' },
                  { key: 'country', label: 'Location' },
                  { key: 'priority', label: 'Priority' },
                  { key: 'status', label: 'Status' },
                  { key: 'demand_signal', label: 'Signal' },
                  { key: 'created_at', label: 'Added' },
                ].map(({ key, label }) => (
                  <th
                    key={key}
                    onClick={() => toggleSort(key)}
                    className="px-4 py-3 text-left text-xs font-medium cursor-pointer hover:text-gray-200 transition-colors select-none"
                  >
                    <div className="flex items-center gap-1">
                      {label}
                      {filters.sort_by === key && (
                        <ArrowUpDown className="w-3 h-3 text-indigo-400" />
                      )}
                    </div>
                  </th>
                ))}
                <th className="px-4 py-3 w-10"></th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="8" className="px-4 py-12 text-center text-gray-500">
                    <div className="animate-spin w-6 h-6 border-2 border-indigo-400 border-t-transparent rounded-full mx-auto" />
                  </td>
                </tr>
              ) : data.leads.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-4 py-12 text-center text-gray-500">
                    No leads found. Adjust your filters or run a scrape.
                  </td>
                </tr>
              ) : (
                data.leads.map((lead) => (
                  <tr
                    key={lead.id}
                    onClick={() => setSelected(lead)}
                    className="border-b border-gray-800/50 hover:bg-gray-800/30 cursor-pointer transition-colors"
                  >
                    <td className="px-4 py-3">
                      <div>
                        <p className="font-medium text-gray-100 truncate max-w-[200px]">{lead.company}</p>
                        {lead.job_title && (
                          <p className="text-xs text-gray-500 truncate max-w-[200px]">{lead.job_title}</p>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-400">{lead.source_name}</td>
                    <td className="px-4 py-3 text-xs">
                      <span className="text-gray-300">{lead.city}</span>
                      {lead.country && (
                        <span className="text-gray-500">, {lead.country}</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-0.5 rounded text-xs border ${
                          PRIORITY_STYLES[lead.priority] || PRIORITY_STYLES.C
                        }`}
                      >
                        {lead.priority}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs ${
                          STATUS_STYLES[lead.status] || STATUS_STYLES.new
                        }`}
                      >
                        {lead.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-400 truncate max-w-[200px]">
                      {lead.demand_signal}
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-500">
                      {new Date(lead.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDelete(lead.id)
                        }}
                        className="text-gray-600 hover:text-red-400 transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {data.total_pages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-800">
            <p className="text-xs text-gray-500">
              Showing {(data.page - 1) * data.per_page + 1}-
              {Math.min(data.page * data.per_page, data.total)} of {data.total}
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setFilters((p) => ({ ...p, page: p.page - 1 }))}
                disabled={data.page <= 1}
                className="p-1.5 rounded-lg border border-gray-700 disabled:opacity-30 hover:bg-gray-800 transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-xs text-gray-400">
                Page {data.page} of {data.total_pages}
              </span>
              <button
                onClick={() => setFilters((p) => ({ ...p, page: p.page + 1 }))}
                disabled={data.page >= data.total_pages}
                className="p-1.5 rounded-lg border border-gray-700 disabled:opacity-30 hover:bg-gray-800 transition-colors"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Detail Panel */}
      {selected && (
        <LeadDetailPanel
          lead={selected}
          options={options}
          onUpdate={handleUpdate}
          onClose={() => setSelected(null)}
        />
      )}
    </div>
  )
}
