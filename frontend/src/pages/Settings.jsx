import { useState, useEffect } from 'react'
import { Save, Terminal, Clock, Globe, RefreshCw, Webhook, Briefcase, Search, MapPin, Plus, X, Database } from 'lucide-react'
import { getConfig, saveConfig } from '../lib/api'
import { useToast } from '../hooks/useToast'

function ChipInput({ items, setItems, placeholder }) {
  const [input, setInput] = useState('')

  const addItem = (val) => {
    const v = val.trim()
    if (v && !items.includes(v)) setItems([...items, v])
    setInput('')
  }

  return (
    <div className="space-y-3">
      {items.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {items.map((item) => (
            <span key={item} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-indigo-500/20 text-indigo-300 text-sm font-medium">
              {item}
              <button onClick={() => setItems(items.filter((i) => i !== item))} className="hover:text-white">
                <X className="w-3.5 h-3.5" />
              </button>
            </span>
          ))}
        </div>
      )}
      <div className="flex gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addItem(input) } }}
          placeholder={placeholder}
          className="flex-1"
        />
        <button
          onClick={() => addItem(input)}
          className="px-4 py-3 bg-gray-800 border border-gray-700 rounded-xl hover:bg-gray-700 transition-colors text-gray-300"
        >
          <Plus className="w-5 h-5" />
        </button>
      </div>
    </div>
  )
}

export default function Settings() {
  const [config, setConfig] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const toast = useToast()

  useEffect(() => {
    getConfig()
      .then(setConfig)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      await saveConfig(config)
      toast.success('Settings saved')
    } catch (err) {
      toast.error('Failed to save: ' + err.message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-full">
      <div className="animate-spin w-10 h-10 border-3 border-indigo-500 border-t-transparent rounded-full" />
    </div>
  )

  if (error) return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-8 text-center">
        <p className="text-lg text-red-400 mb-5">{error}</p>
        <button
          onClick={() => {
            setError(null)
            setLoading(true)
            getConfig()
              .then(setConfig)
              .catch(e => setError(e.message))
              .finally(() => setLoading(false))
          }}
          className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 rounded-xl text-base text-white font-medium transition-colors"
        >
          Retry
        </button>
      </div>
    </div>
  )

  return (
    <div className="p-8 space-y-8 max-w-3xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-gray-100">Settings</h1>
        <p className="text-base text-gray-500 mt-1">Configure scraper behavior and integrations</p>
      </div>

      {/* LLM / Gemini */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/15 flex items-center justify-center">
            <Terminal className="w-5 h-5 text-indigo-400" />
          </div>
          <h2 className="text-lg font-semibold text-gray-100">LLM Enrichment</h2>
        </div>
        <div>
          <label>Gemini CLI Command</label>
          <input
            type="text"
            value={config?.gemini_command || ''}
            onChange={(e) => setConfig(c => ({ ...c, gemini_command: e.target.value }))}
            placeholder="gemini"
            className="w-full font-mono"
          />
          <p className="text-sm text-gray-500 mt-2">Path or command name for the Gemini CLI binary</p>
        </div>
      </div>

      {/* Scraping behavior */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/15 flex items-center justify-center">
            <Clock className="w-5 h-5 text-indigo-400" />
          </div>
          <h2 className="text-lg font-semibold text-gray-100">Scraping Behavior</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div>
            <label>Request Delay (seconds)</label>
            <input
              type="number"
              min="0.5"
              max="10"
              step="0.5"
              value={config?.request_delay ?? 1.5}
              onChange={(e) => setConfig(c => ({ ...c, request_delay: parseFloat(e.target.value) }))}
              className="w-full"
            />
            <p className="text-sm text-gray-500 mt-2">Delay between requests (be respectful to servers)</p>
          </div>
          <div>
            <label>Default Page Limit</label>
            <input
              type="number"
              min="1"
              max="20"
              value={config?.default_page_limit ?? 3}
              onChange={(e) => setConfig(c => ({ ...c, default_page_limit: parseInt(e.target.value) }))}
              className="w-full"
            />
            <p className="text-sm text-gray-500 mt-2">Pages to scrape per query by default</p>
          </div>
        </div>
      </div>

      {/* CORS / Server */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/15 flex items-center justify-center">
            <Globe className="w-5 h-5 text-indigo-400" />
          </div>
          <h2 className="text-lg font-semibold text-gray-100">Server / CORS</h2>
        </div>
        <div>
          <label>Allowed Origins (one per line)</label>
          <textarea
            value={(config?.cors_origins || []).join('\n')}
            onChange={(e) => setConfig(c => ({ ...c, cors_origins: e.target.value.split('\n').map(s => s.trim()).filter(Boolean) }))}
            rows={4}
            className="w-full resize-none font-mono"
          />
          <p className="text-sm text-gray-500 mt-2">Frontend origins allowed to connect to the API</p>
        </div>
      </div>

      {/* ── Search Preferences ─────────────────────── */}

      {/* Job Titles */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/15 flex items-center justify-center">
            <Briefcase className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-100">Job Titles</h2>
            <p className="text-sm text-gray-500">Target roles you're looking for across all sources</p>
          </div>
        </div>
        <ChipInput
          items={config?.job_titles || []}
          setItems={(v) => setConfig(c => ({ ...c, job_titles: v }))}
          placeholder="Add a job title (e.g. 3D Artist)..."
        />
      </div>

      {/* Search Queries (per source) */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/15 flex items-center justify-center">
            <Search className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-100">Search Queries</h2>
            <p className="text-sm text-gray-500">Default queries per source — pre-filled when you launch a scrape</p>
          </div>
        </div>
        {['linkedin', 'upwork', 'artstation', 'wamda'].map((source) => (
          <div key={source} className="space-y-2">
            <label className="text-base font-medium text-gray-300 capitalize">{source}</label>
            <ChipInput
              items={config?.search_queries?.[source] || []}
              setItems={(v) => setConfig(c => ({
                ...c,
                search_queries: { ...(c.search_queries || {}), [source]: v },
              }))}
              placeholder={`Add ${source} query...`}
            />
          </div>
        ))}
      </div>

      {/* Regions */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/15 flex items-center justify-center">
            <MapPin className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-100">Regions</h2>
            <p className="text-sm text-gray-500">Target locations for LinkedIn and other geo-aware scrapers</p>
          </div>
        </div>
        <ChipInput
          items={config?.regions || []}
          setItems={(v) => setConfig(c => ({ ...c, regions: v }))}
          placeholder="Add a region (e.g. United Arab Emirates)..."
        />
      </div>

      {/* Enabled Sources */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/15 flex items-center justify-center">
            <Database className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-100">Enabled Sources</h2>
            <p className="text-sm text-gray-500">Which scrapers are active by default</p>
          </div>
        </div>
        <div className="space-y-3">
          {['linkedin', 'upwork', 'artstation', 'wamda'].map((source) => (
            <label key={source} className="flex items-center gap-4 cursor-pointer group p-4 rounded-xl hover:bg-gray-800/50 transition-colors border border-transparent hover:border-gray-800 mb-0">
              <input
                type="checkbox"
                checked={(config?.enabled_sources || []).includes(source)}
                onChange={(e) => {
                  const current = config?.enabled_sources || []
                  setConfig(c => ({
                    ...c,
                    enabled_sources: e.target.checked
                      ? [...current, source]
                      : current.filter(s => s !== source),
                  }))
                }}
                className="w-5 h-5 rounded border-gray-600 bg-gray-800 text-indigo-500 focus:ring-indigo-500 cursor-pointer"
              />
              <span className="text-base text-gray-200 font-medium capitalize group-hover:text-gray-100 transition-colors">{source}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Webhooks */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/15 flex items-center justify-center">
            <Webhook className="w-5 h-5 text-indigo-400" />
          </div>
          <h2 className="text-lg font-semibold text-gray-100">Webhook Notifications</h2>
        </div>
        <div>
          <label>Webhook URL</label>
          <input
            type="url"
            value={config?.webhook_url || ''}
            onChange={(e) => setConfig(c => ({ ...c, webhook_url: e.target.value || null }))}
            placeholder="https://your-service.com/webhook"
            className="w-full font-mono"
          />
          <p className="text-sm text-gray-500 mt-2">Receives POST requests with JSON payload on configured events</p>
        </div>
        <div className="space-y-4">
          {[
            { key: 'webhook_on_job_complete', label: 'Notify when scrape job completes', desc: 'Includes job ID, source, lead counts' },
            { key: 'webhook_on_new_leads', label: 'Notify when new leads are found', desc: 'Fires per scrape run with new lead count' },
          ].map(({ key, label, desc }) => (
            <label key={key} className="flex items-start gap-4 cursor-pointer group p-4 rounded-xl hover:bg-gray-800/50 transition-colors border border-transparent hover:border-gray-800 mb-0">
              <input
                type="checkbox"
                checked={!!config?.[key]}
                onChange={(e) => setConfig(c => ({ ...c, [key]: e.target.checked }))}
                className="mt-1 w-5 h-5 rounded border-gray-600 bg-gray-800 text-indigo-500 focus:ring-indigo-500 cursor-pointer"
              />
              <div>
                <span className="text-base text-gray-200 font-medium group-hover:text-gray-100 transition-colors">{label}</span>
                <p className="text-sm text-gray-500 mt-0.5">{desc}</p>
              </div>
            </label>
          ))}
        </div>
        {config?.webhook_url && (
          <div className="bg-gray-800/50 rounded-xl p-4 text-sm">
            <span className="text-gray-300 font-semibold">Payload example:</span>
            <pre className="mt-2 text-gray-500 font-mono text-sm leading-relaxed">{JSON.stringify({ event: "job_completed", job_id: 42, source: "linkedin", new_leads: 15 }, null, 2)}</pre>
          </div>
        )}
      </div>

      {/* Save button — big and clear */}
      <div className="flex justify-end pb-4">
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-3 px-8 py-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-2xl text-lg font-semibold text-white transition-colors"
        >
          {saving ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </div>
  )
}
