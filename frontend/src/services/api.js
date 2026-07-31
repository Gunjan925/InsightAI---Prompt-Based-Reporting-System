// services/api.js
// Creates and exports a pre-configured Axios instance used by all service
// modules (auth, upload, report).
//
// Configuration:
//   - baseURL: '/api'  →  all requests go to /api/... which Vite proxies
//                         to http://localhost:8000/api/... in development.
//   - Request interceptor: automatically attaches the JWT Bearer token
//     from localStorage to every outgoing request.
//   - Response interceptor: on 401 Unauthorized, clears the stored token
//     and redirects to /login (session expired or invalid token).

import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
})

// ── Request Interceptor: attach JWT ──────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('insightai_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ── Response Interceptor: handle 401 ─────────────────────────────────────
// api.interceptors.response.use(
//   (response) => response,
//   (error) => {
//     if (error.response?.status === 401) {
//       // Clear stale session and send user to login
//       localStorage.removeItem('insightai_token')
//       localStorage.removeItem('insightai_user')
//       window.location.href = '/login'
//     }
//     return Promise.reject(error)
//   }
// )
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      error.response?.status === 401 &&
      !error.config.url.includes('/auth/login')
    ) {
      localStorage.removeItem('insightai_token')
      localStorage.removeItem('insightai_user')
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

export default api