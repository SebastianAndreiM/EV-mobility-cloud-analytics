import { apiClient } from "./client";

export interface ChargingSession {
  id: number;
  vehicle_id: string;
  charger_id: string;
  charger_type: string;
  status: string;
  energy_kwh: number;
  duration_minutes: number;
  temperature_c: number;
  is_anomaly: boolean;
  start_time: string;
  cost_eur: number;
}

export interface Paginated {
  total: number;
  page: number;
  page_size: number;
  items: ChargingSession[];
}

export interface SessionFilters {
  page?: number;
  page_size?: number;
  charger_type?: string;
  status?: string;
  min_temperature?: number;
  max_temperature?: number;
  anomaly_only?: boolean;
}

export async function generateData(count: number, seed?: number) {
  const { data } = await apiClient.post("/data/generate", { count, seed });
  return data;
}

export async function getSessions(filters: SessionFilters = {}) {
  const { data } = await apiClient.get<Paginated>("/data/sessions", { params: filters });
  return data;
}

export async function deleteAllSessions() {
  const { data } = await apiClient.delete("/data/sessions");
  return data;
}
