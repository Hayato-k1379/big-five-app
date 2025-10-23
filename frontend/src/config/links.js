const DEFAULT_LEGAL_BASE_URL = 'https://big-five-app-of9f.onrender.com';

export const LEGAL_BASE_URL = import.meta.env.VITE_LEGAL_BASE_URL || DEFAULT_LEGAL_BASE_URL;

export const legalLinks = {
  privacy: `${LEGAL_BASE_URL.replace(/\/$/, '')}/legal/privacy/`,
  terms: `${LEGAL_BASE_URL.replace(/\/$/, '')}/legal/terms/`,
  disclaimer: `${LEGAL_BASE_URL.replace(/\/$/, '')}/legal/disclaimer/`,
  tokushoho: `${LEGAL_BASE_URL.replace(/\/$/, '')}/legal/tokushoho/`
};
