import axios from 'axios';

const FALLBACK_BASE_URL = 'http://127.0.0.1:8000/api';

export const normalizeBaseUrl = (baseUrl) => {
  if (!baseUrl) {
    return '';
  }
  const trimmed = baseUrl.trim();
  return trimmed.endsWith('/') ? trimmed.slice(0, -1) : trimmed;
};

const envBaseUrl = normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL);
export const apiBaseUrl = envBaseUrl || FALLBACK_BASE_URL;

if (!envBaseUrl && import.meta.env.DEV) {
  console.warn(
    '[apiClient] VITE_API_BASE_URL is not set. Falling back to http://127.0.0.1:8000/api. '
      + 'Set this variable in Vercel/Render environments to avoid accidental relative requests.'
  );
}

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
});

export const ensureArray = (payload, contextLabel = 'response') => {
  if (Array.isArray(payload)) {
    return payload;
  }
  if (payload && Array.isArray(payload.results)) {
    return payload.results;
  }
  console.error(`[apiClient] Unexpected ${contextLabel} format; returning empty array`, payload);
  return [];
};
