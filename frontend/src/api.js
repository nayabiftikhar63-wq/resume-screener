// Thin fetch wrapper for the FastAPI backend.
// In dev the path `/api/...` is proxied via vite.config.js.
// In production the backend can serve the built SPA from the same origin.

const BASE = import.meta.env.VITE_API_BASE || '';

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options);
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch {
      // ignore
    }
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // Jobs
  listJobs: () => request('/api/jobs'),
  getJob: (id) => request(`/api/jobs/${id}`),
  createJob: (body) =>
    request('/api/jobs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  deleteJob: (id) => request(`/api/jobs/${id}`, { method: 'DELETE' }),

  // Applications
  applyToJob: (jobId, formData) =>
    request(`/api/jobs/${jobId}/apply`, { method: 'POST', body: formData }),
  listApplications: (jobId) => request(`/api/jobs/${jobId}/applications`),

  // Screening
  screenAll: (jobId, { force = false } = {}) =>
    request(`/api/jobs/${jobId}/screen${force ? '?force=true' : ''}`, {
      method: 'POST',
    }),
  screenOne: (appId) =>
    request(`/api/applications/${appId}/screen`, { method: 'POST' }),

  // Email drafting
  draftEmail: (appId, kind = 'interview') =>
    request(`/api/applications/${appId}/draft-email?kind=${kind}`, {
      method: 'POST',
    }),

  // Stats
  getStats: () => request('/api/stats'),
};
