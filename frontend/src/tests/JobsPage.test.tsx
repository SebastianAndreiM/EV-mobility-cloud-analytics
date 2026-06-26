import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import JobsPage from "../pages/JobsPage";
import * as jobsApi from "../api/jobsApi";

vi.mock("../api/jobsApi");

describe("JobsPage", () => {
  it("renders queued/running/completed jobs", async () => {
    vi.mocked(jobsApi.getJobs).mockResolvedValue([
      { id: 1, job_type: "train_duration_model", status: "completed", detail: "v1", created_at: "2024-01-01", updated_at: "2024-01-01" },
      { id: 2, job_type: "train_anomaly_model", status: "running", detail: null, created_at: "2024-01-01", updated_at: "2024-01-01" },
      { id: 3, job_type: "train_duration_model", status: "queued", detail: null, created_at: "2024-01-01", updated_at: "2024-01-01" },
    ]);
    render(<JobsPage />);
    await waitFor(() => expect(screen.getByText("completed")).toBeInTheDocument());
    expect(screen.getByText("running")).toBeInTheDocument();
    expect(screen.getByText("queued")).toBeInTheDocument();
  });
});
