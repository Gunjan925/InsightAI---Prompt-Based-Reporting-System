// services/report.js
// Provides functions to interact with the report-related FastAPI endpoints.
//
// Endpoints used:
//   POST /api/report/generate          → Trigger AI report generation
//   GET  /api/report/{id}              → Fetch a specific report
//   GET  /api/report/{id}/download     → Download report as HTML file
//   GET  /api/history                  → List all reports for the current user
//   GET  /api/dashboard/stats          → Dashboard aggregated statistics

import api from './api'

// Send a report generation request to the AI pipeline.
// file_id: number  – ID returned by uploadDataset()
// prompt:  string  – Natural language analysis instruction
// Returns: ReportResponse { id, user_id, file_id, prompt, report_title, summary, content, created_at }
export async function generateReport(fileId, prompt) {
  const res = await api.post('/report/generate', { file_id: fileId, prompt })
  return res.data
}

// Fetch a previously generated report by its numeric ID.
// Returns: ReportResponse
export async function getReport(reportId) {
  const res = await api.get(`/report/${reportId}`)
  return res.data
}

// Download the report as an HTML file via the browser's download mechanism.
// Uses a temporary anchor element so the browser triggers a file-save dialog.
export async function downloadReport(reportId) {
  const res = await api.get(`/report/${reportId}/download`, {
    responseType: 'blob',           // Receive raw binary blob
  })

  // Create an object URL from the blob and trigger download
  const url     = window.URL.createObjectURL(new Blob([res.data], { type: 'text/html' }))
  const anchor  = document.createElement('a')
  anchor.href   = url
  anchor.download = `report_${reportId}.html`
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  window.URL.revokeObjectURL(url)
}

// Retrieve all historical reports for the authenticated user.
// Returns: ReportListItem[] { id, file_id, filename, report_title, summary, created_at }
export async function getHistory() {
  const res = await api.get('/history')
  return res.data
}

// Fetch aggregated dashboard statistics.
// Returns: DashboardStats { total_files_uploaded, total_reports_generated,
//                           latest_report_title, latest_report_date,
//                           file_type_distribution: { csv: n, xlsx: n, ... } }
export async function getDashboardStats() {
  const res = await api.get('/dashboard/stats')
  return res.data
}