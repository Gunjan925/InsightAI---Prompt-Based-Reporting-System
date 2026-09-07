// services/chat.js
// Interacts with backend MySQL chat persistence and QA endpoints.

import api from './api'

export async function getChatSessions(fileId) {
  const res = await api.get(`/chat/sessions/${fileId}`)
  return res.data
}

export async function createChatSession(fileId, title = "New Discussion") {
  const res = await api.post('/chat/sessions', { file_id: fileId, title })
  return res.data
}

export async function deleteChatSession(sessionId) {
  const res = await api.delete(`/chat/sessions/${sessionId}`)
  return res.data
}

export async function askChatQuestion(fileId, query, sessionId = null) {
  const res = await api.post('/chat/ask', {
    file_id: fileId,
    query: query,
    session_id: sessionId
  })
  return res.data
}
