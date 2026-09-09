const BASE = '/api'

async function req(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options)
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`${res.status} ${res.statusText}: ${body}`)
  }
  const contentType = res.headers.get('content-type') || ''
  if (contentType.includes('application/json')) return res.json()
  return res
}

export const api = {
  uploadVideo: (file) => {
    const form = new FormData()
    form.append('file', file)
    return req('/jobs', { method: 'POST', body: form })
  },
  getJob: (id) => req(`/jobs/${id}`),
  prepare: (id, crop) =>
    req(`/jobs/${id}/prepare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(crop ? { crop } : {}),
    }),
  frameUrl: (id) => `${BASE}/jobs/${id}/frame`,
  transcribe: (id, language = 'auto') =>
    req(`/jobs/${id}/transcribe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ language }),
    }),
  getTranscript: (id) => req(`/jobs/${id}/transcript`),
  updateTranscript: (id, segments) =>
    req(`/jobs/${id}/transcript`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ segments }),
    }),
  translate: (id, targetLang) =>
    req(`/jobs/${id}/translate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_lang: targetLang }),
    }),
  getTranslations: (id) => req(`/jobs/${id}/translations`),
  updateTranslations: (id, lang, translations) =>
    req(`/jobs/${id}/translations/${lang}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ translations }),
    }),
  getStyles: (id) => req(`/jobs/${id}/styles`),
  render: (id, tracks) =>
    req(`/jobs/${id}/render`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tracks }),
    }),
  getRenders: (id) => req(`/jobs/${id}/renders`),
  downloadUrl: (id, filename) => `${BASE}/jobs/${id}/renders/${filename}/download`,
}
