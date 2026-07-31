// services/upload.js
// Provides a function to upload a dataset file (CSV or Excel) to the backend.
//
// Endpoint used:
//   POST /api/upload  (multipart/form-data)
//
// The upload is sent as FormData so that the file binary is transmitted
// alongside the filename. An optional onUploadProgress callback allows the
// caller (UploadProgress component) to display a real-time progress bar.
//
// Returns: UploadResponse { id, filename, file_size, mime_type, created_at }
// The returned `id` is the file_id needed when calling generateReport().

import api from './api'

// uploadDataset(file, onProgress?)
//   file       – browser File object (from <input type="file"> or drag-drop)
//   onProgress – optional callback(percent: number) for progress reporting
export async function uploadDataset(file, onProgress) {
  const formData = new FormData()
  formData.append('file', file)

  const res = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (event) => {
      if (onProgress && event.total) {
        const percent = Math.round((event.loaded / event.total) * 100)
        onProgress(percent)
      }
    },
  })
  return res.data
}