import { useState, useEffect } from 'react'
import { getStats } from '../lib/api'
import { TrendingUp, Users, Clock, Zap } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd', '#818cf8', '#4f46e5', '#7c3aed']

function StatCard({ icon: Icon, label, value, sub, color = 'indigo' }) {
  const colorMap = {
    indigo: 'bg-indigo-500/10 text-indigo-400',
    emerald: 'bg-emerald-500/10 text-emerald-400',
    amber: 'bg-amber-500/10 text-amber-400',
    rose: 'bg-rose-500/10 text-rose-400',
  }
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex items-center gap-3 mb-3">
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${colorMap[color]}`}>
          <Icon className="w-4 h-4" />
        </div>
        <span className="text-sm text-gray-400">{label}</span>
      </div>
      <p className="text-2xl font-bold">{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  )
}

export default function Dashboard({ ws }) {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  // Refresh stats when scrape job completes
  useEffect(() => {
    const latest = ws.messages[0]
    if (latest?.status === 'completed') {
      getStats().then(setStats).catch(console.error)
    }
  }, [ws.messages])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin w-8 h-8 border-2 border-indigo-400 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p>Could not load stats. Make sure the API server is running.</p>
        <p className="text-sm mt-2">Run: <code className="bg-gray-800 px-2 py-1 rounded">python run.py</code></p>
      </div>
    )
  }

  const sourceData = Object.entries(stats.by_source || {}).map(([name, count]) => ({
    name: name || 'Unknown',
    value: count,
  }))

  const priorityData = Object.entries(stats.by_priority || {}).map(([name, count]) => ({
    name,
    value: count,
  }))

  const countryData = Object.entries(stats.by_country || {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([name, count]) => ({ name: name || 'Unknown', count }))

  return (
    <div className="p-6 space-y-6 max-w-7xl">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Overview of your lead pipeline</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Users} label="Total Leads" value={stats.total_leads} color="indigo" />
        <StatCard icon={Zap} label="Today" value={stats.leads_today} color="emerald" />
        <StatCard icon={TrendingUp} label="This Week" value={stats.leads_this_week} color="amber" />
        <StatCard
          icon={Clock}
          label="Sources Active"
          value={Object.keys(stats.by_source || {}).length}
          color="rose"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* By Source */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="text-sm font-medium text-gray-400 mb-4">Leads by Source</h3>
          {sourceData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={sourceData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {sourceData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8 }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-600 text-center py-12">No data yet. Run a scrape to get started.</p>
          )}
        </div>

        {/* By Country */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="text-sm font-medium text-gray-400 mb-4">Top Countries</h3>
          {countryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={countryData} layout="vertical" margin={{ left: 80 }}>
                <XAxis type="number" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                <YAxis
                  type="category"
                  dataKey="name"
                  tick={{ fill: '#9ca3af', fontSize: 12 }}
                  width={75}
                />
                <Tooltip
                  contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8 }}
                />
                <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-600 text-center py-12">No data yet.</p>
          )}
        </div>
      </div>

      {/* Priority breakdown */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 className="text-sm font-medium text-gray-400 mb-4">Priority Breakdown</h3>
        <div className="flex gap-4 flex-wrap">
          {priorityData.map(({ name, value }) => {
            const colorMap = {
              'A+': 'bg-red-500/20 text-red-300 border-red-500/30',
              A: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
              B: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
              C: 'bg-gray-500/20 text-gray-300 border-gray-500/30',
            }
            return (
              <div
                key={name}
                className={`px-4 py-3 rounded-lg border ${colorMap[name] || colorMap.C}`}
              >
                <p className="text-xs opacity-70">Priority {name}</p>
                <p className="text-xl font-bold">{value}</p>
              </div>
            )
          })}
        </div>
      </div>

      {/* Recent Jobs */}
      {stats.recent_jobs?.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="text-sm font-medium text-gray-400 mb-4">Recent Scrape Jobs</h3>
          <div className="space-y-2">
            {stats.recent_jobs.map((job) => (
              <div
                key={job.id}
                className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50"
              >
                <div>
                  <span className="font-medium text-sm">{job.source_name}</span>
                  <span className="text-xs text-gray-500 ml-2">{job.query || 'Default query'}</span>
                </div>
                <div className="flex items-center gap-4 text-xs">
                  <span className="text-emerald-400">+{job.new_leads} new</span>
                  <span className="text-gray-500">{job.duplicates_skipped} dupes</span>
                  <span
                    className={`px-2 py-0.5 rounded-full ${
                      job.status === 'completed'
                        ? 'bg-emerald-500/20 text-emerald-300'
                        : job.status === 'running'
                        ? 'bg-blue-500/20 text-blue-300'
                        : job.status === 'failed'
                        ? 'bg-red-500/20 text-red-300'
                        : 'bg-gray-500/20 text-gray-300'
                    }`}
                  >
                    {job.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
