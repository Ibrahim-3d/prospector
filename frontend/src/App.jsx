import { useState, useEffect, useRef } from 'react'
import { Routes, Route, NavLink, useNavigate, useLocation } from 'react-router-dom'
import { Target, Radar, Database, BarChart3, Settings as SettingsIcon, HelpCircle, X } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import ScrapeControl from './pages/ScrapeControl'
import LeadsTable from './pages/LeadsTable'
import Settings from './pages/Settings'
import { useWebSocket } from './hooks/useWebSocket'

const navItems = [
  { to: '/', icon: BarChart3, label: 'Dashboard' },
  { to: '/scrape', icon: Radar, label: 'Scrape Control' },
  { to: '/leads', icon: Database, label: 'Leads Database' },
  { to: '/settings', icon: SettingsIcon, label: 'Settings' },
]

export default function App() {
  const ws = useWebSocket()
  const navigate = useNavigate()
  const location = useLocation()
  const gKeyTimeout = useRef(null)
  const [gPressed, setGPressed] = useState(false)
  const [showShortcutsHelp, setShowShortcutsHelp] = useState(false)

  useEffect(() => {
    const handleKeyDown = (e) => {
      const tag = document.activeElement?.tagName?.toLowerCase()
      if (['input', 'textarea', 'select'].includes(tag)) return
      if (e.ctrlKey || e.metaKey || e.altKey) return

      if (gPressed) {
        clearTimeout(gKeyTimeout.current)
        setGPressed(false)
        if (e.key === 'd') { e.preventDefault(); navigate('/') }
        if (e.key === 's') { e.preventDefault(); navigate('/scrape') }
        if (e.key === 'l') { e.preventDefault(); navigate('/leads') }
        if (e.key === 'c') { e.preventDefault(); navigate('/settings') }
        return
      }

      if (e.key === 'g') {
        setGPressed(true)
        gKeyTimeout.current = setTimeout(() => setGPressed(false), 500)
        return
      }

      if (e.key === '/' && location.pathname === '/leads') {
        e.preventDefault()
        const searchInput = document.querySelector('input[placeholder*="Search"]') || document.querySelector('input[type="search"]')
        if (searchInput) searchInput.focus()
        return
      }

      if (e.key === '?') {
        e.preventDefault()
        setShowShortcutsHelp(v => !v)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      clearTimeout(gKeyTimeout.current)
    }
  }, [gPressed, navigate, location])

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar — always expanded with labels visible */}
      <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col h-screen shrink-0">
        {/* Header */}
        <div className="p-5 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center">
              <Target className="w-5 h-5 text-indigo-400" />
            </div>
            <div>
              <span className="font-bold text-lg block">LeadsScraper</span>
              <span className="text-xs text-gray-500">Dashboard Mode</span>
            </div>
          </div>
        </div>

        {/* Nav — big clickable items, always labeled */}
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3.5 rounded-xl text-[15px] font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                    : 'text-gray-400 hover:text-gray-100 hover:bg-gray-800/70 border border-transparent'
                }`
              }
            >
              <Icon className="w-5 h-5 shrink-0" />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Footer: WebSocket status + shortcuts */}
        <div className="p-4 border-t border-gray-800 space-y-3">
          <div className="flex items-center gap-3">
            <div
              className={`w-2.5 h-2.5 rounded-full shrink-0 ${ws.connected ? 'bg-green-400' : 'bg-red-400 animate-pulse'}`}
            />
            <span className="text-sm text-gray-400">
              {ws.connected ? 'Live updates active' : 'Reconnecting...'}
            </span>
          </div>
          <button
            onClick={() => setShowShortcutsHelp(true)}
            className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-300 transition-colors w-full"
          >
            <HelpCircle className="w-4 h-4" />
            <span>Keyboard shortcuts</span>
            <kbd className="ml-auto px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-xs text-gray-500 font-mono">?</kbd>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 min-w-0 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Dashboard ws={ws} />} />
          <Route path="/scrape" element={<ScrapeControl ws={ws} />} />
          <Route path="/leads" element={<LeadsTable />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <p className="text-5xl font-bold text-gray-700 mb-3">404</p>
                <p className="text-lg text-gray-500">Page not found</p>
              </div>
            </div>
          } />
        </Routes>
      </main>

      {/* Keyboard shortcuts help overlay */}
      {showShortcutsHelp && (
        <div className="fixed inset-0 bg-black/60 z-[200] flex items-center justify-center p-4"
          onClick={() => setShowShortcutsHelp(false)}>
          <div className="bg-gray-900 border border-gray-700 rounded-2xl p-8 max-w-md w-full shadow-2xl"
            onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-100">Keyboard Shortcuts</h2>
              <button onClick={() => setShowShortcutsHelp(false)} className="text-gray-500 hover:text-gray-300 p-1">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-3">
              {[
                ['/', 'Focus search (on Leads page)'],
                ['g → d', 'Go to Dashboard'],
                ['g → s', 'Go to Scrape Control'],
                ['g → l', 'Go to Leads Database'],
                ['g → c', 'Go to Settings'],
                ['?', 'Toggle this help'],
              ].map(([shortcut, desc]) => (
                <div key={shortcut} className="flex items-center justify-between py-1">
                  <span className="text-sm text-gray-300">{desc}</span>
                  <kbd className="px-2.5 py-1 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-300 font-mono">
                    {shortcut}
                  </kbd>
                </div>
              ))}
            </div>
            <p className="text-sm text-gray-600 mt-6">Shortcuts are disabled when typing in inputs</p>
          </div>
        </div>
      )}
    </div>
  )
}
