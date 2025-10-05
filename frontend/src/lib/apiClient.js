import axios from 'axios';

const normalizeBaseUrl = (baseUrl) => {
  if (!baseUrl) {
    return '/api';
  }
  const trimmed = baseUrl.trim();
  return trimmed.endsWith('/') ? trimmed.slice(0, -1) : trimmed;
};

const baseURL = normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL);

export const apiClient = axios.create({
  baseURL,
});
