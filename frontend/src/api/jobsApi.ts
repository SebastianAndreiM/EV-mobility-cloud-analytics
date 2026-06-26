import { apiClient } from "./client";

export interface Job {
  id: number;
  job_type: string;
  status: string;
  detail: string | null;
  created_at: string;
  updated_at: string;
}

export async function getJobs() {
  const { data } = await apiClient.get<Job[]>("/jobs");
  return data;
}

export async function getJob(id: number) {
  const { data } = await apiClient.get<Job>(`/jobs/${id}`);
  return data;
}
