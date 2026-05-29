const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `API error: ${res.status}`);
  }
  const json = await res.json();
  if (!json.success) throw new Error(json.error?.message || 'API request failed');
  return json.data;
}

export const api = {
  getBusinessTypes: () => request('/business-types'),
  getRegions: () => request('/regions'),
  analyze: (payload) => request('/analyze', { method: 'POST', body: JSON.stringify(payload) }),
  getAnalysis: (analysisId) => request(`/analysis/${analysisId}`),
  getRedzones: ({ business_type_id, region_id, lat, lng, radius = 2000 }) => {
    const params = new URLSearchParams({ business_type_id, radius: String(radius) });
    if (region_id) params.set('region_id', region_id);
    if (lat) params.set('lat', String(lat));
    if (lng) params.set('lng', String(lng));
    return request(`/redzones?${params.toString()}`);
  },
  report: (payload) => request('/report', { method: 'POST', body: JSON.stringify(payload) }),
  chat: (payload) => request('/chat', { method: 'POST', body: JSON.stringify(payload) }),
  compare: (payload) => request('/compare', { method: 'POST', body: JSON.stringify(payload) }),
};
