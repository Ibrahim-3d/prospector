import { useState, useEffect } from 'react'
import { getSources, startScrape, cancelScrape, getScrapeJobs } from '../lib/api'
import {
  Radar, Play, Square, Plus, X, ChevronDown, ChevronUp, Loader2, CheckCircle2, XCircle, Clock,
} from 'lucide-react'

const PRESET_REGIONS = [
  'United Arab Emirates', 'Kuwait', 'Saudi Arabia', 'Qatar', 'Bahrain', 'Oman',
  'London', 'Berlin', 'Paris', 'Amsterdam', 'New York', 'Los Angeles',
  'Toronto', 'Sydney', 'Singapore', 'Remote',
]

const PRESET_QUERIES = {
  linkedin: [
    '3D Artist OR Motion Designer OR CGI',
    'Unreal Engine Developer',
    '3D Animator',
    'Motion Graphics Designer',
    'Creative Director 3D',
    'WebGL Developer',
    'Product Visualization',
    'Architectural Visualization',
    'VFX Artist',
    'Real-time 3D',
  ],
  upwork: [
    '3d-animation', '3d-rendering', 'motion-graphics', 'unreal-engine',
    'webgl', 'product-visualization', 'architectural-visualization',
  ],
  artstation: [],
  wamda: [],
}

function TagInput({ tags, setTags, placeholder, presets = [] }) {
  const [input, setInput] = useState('')
  const [showPresets, setShowPresets] = useState(false)

  const addTag = (tag) => {
    const t = tag.trim()
    if (t && !tags.includes(t)) setTags([...tags, t])
    setInput('')
  }

  return (
    <div>
      <div className="flex flex-wrap gap-1.5 mb-2">
        {tags.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-indigo-500/20 text-indigo-300 text-xs"
          >
            {tag}
            <button onClick={() => setTags(tags.filter((t) => t !== tag))} className="hover:text-white">
              <X className="w-3 h-3" />
            </button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') { e.preventDefault(); addTag(input) }
          }}
          placeholder={placeholder}
          className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
        />
        <button
          onClick={() => addTag(input)}
          className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg hover:bg-gray-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>
      {presets.length > 0 && (
        <div className="mt-2">
          <button
            onClick={() => setShowPresets(!showPresets)}
            className="text-xs text-gray-500 hover:text-gray-300 flex items-center gap-1"
          >
            {showPresets ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            Quick add from presets
          </button>
          {showPresets && (
            <div className="flex flex-wrap gap-1.5 mt-2">
              {presets
                .filter((p) => !tags.includes(p))
                .map((preset) => (
                  <button
                    key={preset}
                    onClick={() => addTag(preset)}
                    className="px-2 py-1 rounded bg-gray-800 text-xs text-gray-400 hover:bg-gray-700 hover:text-gray-200 transition-colors border border-gray-700"
                  >
                    + {preset}
                  </button>
                ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function JobCard({ job, onCancel }) {
  const statusStyles = {
    pending: 'bg-gray-500/20 text-gray-300',
    running: 'bg-blue-500/20 text-blue-300',
    completed: 'bg-emerald-500/20 text-emerald-300',
    failed: 'bg-red-500/20 text-red-300',
    cancelled: 'bg-orange-500/20 text-orange-300',
  }

  const StatusIcon = {
    pending: Clock,
    running: Loader2,
    completed: CheckCircle2,
    failed: XCircle,
    cancelled: Square,
  }[job.status] || Clock

  return (
    <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <StatusIcon
            className={`w-4 h-4 ${job.status === 'running' ? 'animate-spin text-blue-400' : ''} ${
              job.status === 'completed' ? 'text-emerald-400' : ''
            } ${job.status === 'failed' ? 'text-red-400' : ''}`}
          />
          <span className="font-medium text-sm">{job.source_name}</span>
          <span className={`px-2 py-0.5 rounded-full text-xs ${statusStyles[job.status]}`}>
            {job.status}
          </span>
        </div>
        {job.status === 'running' && (
          <button
            onClick={() => onCancel(job.id)}
            className="text-xs text-red-400 hover:text-red-300 flex items-center gap-1"
          >
            <Square className="w-3 h-3" /> Cancel
          </button>
        )}
      </div>

      {job.query && <p className="text-xs text-gray-500 mb-2 truncate">Query: {job.query}</p>}

      {/* Progress bar */}
      {job.status === 'running' && (
        <div className="mb-2">
          <div className="flex justify-between text-xs text-gray-400 mb-1">
            <span>{job.progress_message || 'Working...'}</span>
            <span>{job.progress}%</span>
          </div>
          <div className="w-full h-1.5 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-500 rounded-full transition-all duration-500"
              style={{ width: `${job.progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Results */}
      <div className="flex gap-4 text-xs text-gray-400">
        <span>Found: <span className="text-gray-200">{job.total_found}</span></span>
        <span>New: <span className="text-emerald-400">{job.new_leads}</span></span>
        <span>Dupes: <span className="text-yellow-400">{job.duplicates_skipped}</span></span>
        {job.errors > 0 && <span>Errors: <span className="text-red-400">{job.errors}</span></span>}
        {job.duration_seconds > 0 && (
          <span>Time: {Math.round(job.duration_seconds)}s</span>
        )}
      </div>
    </div>
  )
}

export default function ScrapeControl({ ws }) {
  const [sources, setSources] = useState([])
  const [jobs, setJobs] = useState([])
  const [selectedSource, setSelectedSource] = useState('')
  const [queries, setQueries] = useState([])
  const [regions, setRegions] = useState([])
  const [pageLimit, setPageLimit] = useState(3)
  const [useLLM, setUseLLM] = useState(true)
  const [launching, setLaunching] = useState(false)

  // Load sources and jobs
  useEffect(() => {
    getSources().then(setSources).catch(console.error)
    getScrapeJobs().then(setJobs).catch(console.error)
  }, [])

  // Update jobs from WS messages
  useEffect(() => {
    const latest = ws.messages[0]
    if (!latest?.job_id) return

    setJobs((prev) => {
      const idx = prev.findIndex((j) => j.id === latest.job_id)
      if (idx >= 0) {
        const updated = [...prev]
        updated[idx] = { ...updated[idx], ...latest }
        return updated
      }
      return prev
    })
  }, [ws.messages])

  const handleLaunch = async () => {
    if (!selectedSource) return
    setLaunching(true)
    try {
      const job = await startScrape({
        source_slug: selectedSource,
        queries,
        regions,
        page_limit: pageLimit,
        use_llm: useLLM,
      })
      setJobs((prev) => [job, ...prev])
    } catch (err) {
      alert(`Failed to start scrape: ${err.message}`)
    }
    setLaunching(false)
  }

  const handleCancel = async (jobId) => {
    try {
      await cancelScrape(jobId)
      setJobs((prev) =>
        prev.map((j) => (j.id === jobId ? { ...j, status: 'cancelled' } : j))
      )
    } catch (err) {
      alert(`Cancel failed: ${err.message}`)
    }
  }

  const selectedSourceObj = sources.find((s) => s.slug === selectedSource)

  return (
    <div className="p-6 max-w-5xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Radar className="w-6 h-6 text-indigo-400" />
          Scrape Control
        </h1>
        <p className="text-sm text-gray-500 mt-1">Configure and launch scraping jobs with full control</p>
      </div>

      {/* Source Selection */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-5">
        <h2 className="text-sm font-medium text-gray-300">1. Select Source</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {sources.map((source) => (
            <button
              key={source.slug}
              onClick={() => {
                setSelectedSource(source.slug)
                setQueries([])
                setRegions([])
              }}
              disabled={!source.enabled}
              className={`p-3 rounded-xl border text-left transition-all ${
                selectedSource === source.slug
                  ? 'border-indigo-500 bg-indigo-500/10'
                  : source.enabled
                  ? 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
                  : 'border-gray-800 bg-gray-900 opacity-40 cursor-not-allowed'
              }`}
            >
              <p className="font-medium text-sm">{source.name}</p>
              <p className="text-xs text-gray-500 mt-1">{source.total_leads} leads</p>
            </button>
          ))}
        </div>

        {/* Query Configuration */}
        {selectedSource && (
          <>
            <hr className="border-gray-800" />
            <h2 className="text-sm font-medium text-gray-300">2. Configure Search</h2>

            {/* Queries */}
            {['linkedin', 'upwork'].includes(selectedSource) && (
              <div>
                <label className="text-xs text-gray-400 block mb-2">
                  Search Queries (job titles, keywords, boolean strings)
                </label>
                <TagInput
                  tags={queries}
                  setTags={setQueries}
                  placeholder="Add a search query..."
                  presets={PRESET_QUERIES[selectedSource] || []}
                />
              </div>
            )}

            {/* Regions */}
            {selectedSource === 'linkedin' && (
              <div>
                <label className="text-xs text-gray-400 block mb-2">
                  Regions / Locations
                </label>
                <TagInput
                  tags={regions}
                  setTags={setRegions}
                  placeholder="Add a region..."
                  presets={PRESET_REGIONS}
                />
              </div>
            )}

            {/* Advanced settings */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-gray-400 block mb-2">Pages per query</label>
                <input
                  type="number"
                  value={pageLimit}
                  onChange={(e) => setPageLimit(Number(e.target.value))}
                  min={1}
                  max={10}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="text-xs text-gray-400 block mb-2">LLM Enrichment</label>
                <button
                  onClick={() => setUseLLM(!useLLM)}
                  className={`w-full px-3 py-2 rounded-lg text-sm border transition-colors ${
                    useLLM
                      ? 'bg-indigo-500/20 border-indigo-500/50 text-indigo-300'
                      : 'bg-gray-800 border-gray-700 text-gray-400'
                  }`}
                >
                  {useLLM ? 'Enabled (Gemini CLI)' : 'Disabled (faster, no scoring)'}
                </button>
              </div>
            </div>

            {/* Launch Button */}
            <button
              onClick={handleLaunch}
              disabled={launching}
              className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium flex items-center justify-center gap-2 transition-colors"
            >
              {launching ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              {launching ? 'Launching...' : `Launch ${selectedSourceObj?.name || ''} Scrape`}
            </button>
          </>
        )}
      </div>

      {/* Active & Recent Jobs */}
      <div className="space-y-3">
        <h2 className="text-sm font-medium text-gray-400">Scrape Jobs</h2>
        {jobs.length === 0 ? (
          <div className="text-center py-12 text-gray-600">
            <Radar className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p>No scrape jobs yet. Configure a source above and hit launch.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {jobs.map((job) => (
              <JobCard key={job.id} job={job} onCancel={handleCancel} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
