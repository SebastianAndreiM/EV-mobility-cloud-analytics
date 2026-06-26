import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import DashboardPage from "../pages/DashboardPage";
import * as analyticsApi from "../api/analyticsApi";

vi.mock("../api/analyticsApi");

describe("DashboardPage", () => {
  it("displays analytics cards from mocked API", async () => {
    vi.mocked(analyticsApi.getSummary).mockResolvedValue({
      total_sessions: 5000, average_duration: 42.5, average_energy: 30,
      average_power: 50, anomaly_rate: 0.05, completion_rate: 0.6,
      total_energy: 150000, total_cost: 67500,
    });
    render(<DashboardPage />);
    await waitFor(() => expect(screen.getByText("5000")).toBeInTheDocument());
    expect(screen.getByText("Total Sessions")).toBeInTheDocument();
    expect(screen.getByText("5.0%")).toBeInTheDocument();
  });
});
