import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import SessionsPage from "../pages/SessionsPage";
import * as dataApi from "../api/dataApi";

vi.mock("../api/dataApi");

describe("SessionsPage", () => {
  it("renders rows from mocked API", async () => {
    vi.mocked(dataApi.getSessions).mockResolvedValue({
      total: 1, page: 1, page_size: 20,
      items: [{
        id: 101, vehicle_id: "EV-1234", charger_id: "CHG-F-500", charger_type: "fast",
        status: "completed", energy_kwh: 30, duration_minutes: 40, temperature_c: 20,
        is_anomaly: false, start_time: "2024-01-01", cost_eur: 13.5,
      }],
    });
    render(<SessionsPage />);
    await waitFor(() => expect(screen.getByText("EV-1234")).toBeInTheDocument());
    expect(screen.getByText("CHG-F-500")).toBeInTheDocument();
  });
});
