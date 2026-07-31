// services/auth.js
// Provides functions to call the FastAPI authentication endpoints.
//
// Endpoints used:
//   POST /api/auth/register  → Create a new account
//   POST /api/auth/login     → Obtain a JWT access token
//   GET  /api/auth/me        → Get the currently authenticated user's profile
//   POST /api/auth/logout    → Blacklist the current token on the server

import api from './api'

// Register a new user account.
// payload: { username, email, password }
// Returns the new UserResponse object.
export async function registerUser(payload) {
  const res = await api.post('/auth/register', payload)
  return res.data
}

// Log in with email + password.
// payload: { email, password }
// Returns: { access_token, token_type, user: UserResponse }
export async function loginUser(payload) {
  const res = await api.post('/auth/login', payload)
  return res.data
}

// Retrieve the currently logged-in user's profile.
// Requires a valid JWT (auto-attached by api.js interceptor).
// Returns: UserResponse
export async function getMe() {
  const res = await api.get('/auth/me')
  return res.data
}

// Log out: blacklists the current JWT on the server.
// Returns: { message: "Successfully logged out" }
export async function logoutUser() {
  const res = await api.post('/auth/logout')
  return res.data
}