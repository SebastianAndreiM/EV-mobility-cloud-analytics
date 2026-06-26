import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const apiClient = axios.create({ baseURL: API_BASE_URL });

let authToken: string | null = null;

export function setAuthToken(token: string | null) {
  authToken = token;
}

apiClient.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});
