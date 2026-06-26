import { apiClient } from "./client";

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  created_at: string;
}

export async function register(email: string, password: string, full_name?: string) {
  const { data } = await apiClient.post<User>("/auth/register", { email, password, full_name });
  return data;
}

export async function login(email: string, password: string) {
  const { data } = await apiClient.post<{ access_token: string }>("/auth/login", { email, password });
  return data.access_token;
}

export async function getMe() {
  const { data } = await apiClient.get<User>("/auth/me");
  return data;
}
