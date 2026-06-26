import { apiClient } from "./client";

export interface Summary {
  total_sessions: number;
  average_duration: number;
  average_energy: number;
  average_power: number;
  anomaly_rate: number;
  completion_rate: number;
  total_energy: number;
  total_cost: number;
}

export async function getSummary() {
  const { data } = await apiClient.get<Summary>("/analytics/summary");
  return data;
}

export async function getDailyEnergy() {
  const { data } = await apiClient.get<{ day: string; total_energy: number; sessions: number }[]>(
    "/analytics/daily-energy"
  );
  return data;
}

export async function getChargerPerformance() {
  const { data } = await apiClient.get<
    { charger_type: string; charger_id: string; sessions: number; avg_energy: number }[]
  >("/analytics/charger-performance");
  return data;
}

export async function getAnomalies() {
  const { data } = await apiClient.get("/analytics/anomalies");
  return data;
}
