import { apiClient } from "./client";

export interface PredictInput {
  charger_type: string;
  start_battery_percent: number;
  end_battery_percent: number;
  battery_capacity_kwh: number;
  charging_power_kw: number;
  temperature_c: number;
  average_voltage: number;
  average_current: number;
}

export async function trainDuration() {
  const { data } = await apiClient.post("/ml/train-duration-model");
  return data;
}

export async function trainAnomaly() {
  const { data } = await apiClient.post("/ml/train-anomaly-model");
  return data;
}

export async function getMetrics(model_type = "duration") {
  const { data } = await apiClient.get("/ml/metrics", { params: { model_type } });
  return data;
}

export async function predictDuration(input: PredictInput) {
  const { data } = await apiClient.post("/ml/predict-duration", input);
  return data;
}
