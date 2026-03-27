/**
 * API client for the Leads Scraper backend.
 */

const BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

// Sources
export const getSources = () => request('/sources')
export const toggleSource = (id, enabled) =>
  request(`/sources/${id}`, { method: 'PATCH', body: JSON.stringify({ enabled }) })

// Leads
export const getLeads = (params = {}) => {
  const qs = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') qs.set(k, v)
  })
  return request(`/leads?${qs}`)
}

export const getLead = (id) => request(`/leads/${id}`)
export const updateLead = (id, data) =>
  request(`/leads/${id}`, { method: 'PATCH', body: JSON.stringify(data) })
export const deleteLead = (id) =>
  request(`/leads/${id}`, { method: 'DELETE' })
export const getFilterOptions = () => request('/leads/filters/options')

// Scrape Jobs
export const startScrape = (data) =>
  request('/scrape', { method: 'POST', body: JSON.stringify(data) })
export const cancelScrape = (jobId) =>
  request(`/scrape/${jobId}/cancel`, { method: 'POST' })
export const getScrapeJobs = (limit = 20) => request(`/scrape/jobs?limit=${limit}`)
export const getScrapeJob = (id) => request(`/scrape/jobs/${id}`)

// Stats
export const getStats = () => request('/stats')

// Export
export async function exportLeads(filters = {}, format = 'csv') {
  const params = new URLSearchParams()
  params.set('format', format)
  if (filters.source_name) params.set('source_name', filters.source_name)
  if (filters.status) params.set('status', filters.status)
  if (filters.priority) params.set('priority', filters.priority)
  if (filters.country) params.set('country', filters.country)
  if (filters.search) params.set('search', filters.search)

  const res = await fetch(`/api/leads/export?${params}`)
  if (!res.ok) throw new Error('Export failed')
  return res.blob()
}

// Lead creation
export async function createLead(data) {
  const res = await fetch('/api/leads', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Failed to create lead') }
  return res.json()
}

// Bulk operations
export async function bulkUpdateLeads(leadIds, updates) {
  const res = await fetch('/api/leads/bulk', {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lead_ids: leadIds, ...updates }),
  })
  if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Bulk update failed') }
  return res.json()
}

export async function bulkDeleteLeads(leadIds) {
  const res = await fetch('/api/leads/bulk', {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lead_ids: leadIds }),
  })
  if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Bulk delete failed') }
  return res.json()
}

// Tags
export async function getTags() {
  const res = await fetch('/api/tags')
  if (!res.ok) throw new Error('Failed to load tags')
  return res.json()
}

export async function createTag(name, color = '#6366f1') {
  const res = await fetch('/api/tags', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, color }),
  })
  if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Failed to create tag') }
  return res.json()
}

export async function deleteTag(tagId) {
  const res = await fetch(`/api/tags/${tagId}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete tag')
  return res.json()
}

export async function updateLeadTags(leadId, tagIds) {
  const res = await fetch(`/api/leads/${leadId}/tags`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tag_ids: tagIds }),
  })
  if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Failed to update tags') }
  return res.json()
}

// Config
export async function getConfig() {
  const res = await fetch('/api/config')
  if (!res.ok) throw new Error('Failed to load config')
  return res.json()
}

export async function saveConfig(config) {
  const res = await fetch('/api/config', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  })
  if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Failed to save config') }
  return res.json()
}
