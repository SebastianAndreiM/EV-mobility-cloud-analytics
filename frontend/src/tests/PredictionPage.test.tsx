import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import PredictionPage from "../pages/PredictionPage";
import * as mlApi from "../api/mlApi";

vi.mock("../api/mlApi");

describe("PredictionPage", () => {
  it("validates that start battery < end battery", async () => {
    render(<PredictionPage />);
    fireEvent.change(screen.getByLabelText("Start battery %"), { target: { value: "90" } });
    fireEvent.change(screen.getByLabelText("End battery %"), { target: { value: "30" } });
    fireEvent.submit(screen.getByLabelText("predict-form"));
    await waitFor(() =>
      expect(screen.getByText(/Start battery must be lower/i)).toBeInTheDocument()
    );
    expect(mlApi.predictDuration).not.toHaveBeenCalled();
  });

  it("submits a valid prediction and shows result", async () => {
    vi.mocked(mlApi.predictDuration).mockResolvedValue({
      predicted_duration_minutes: 55.4, model_version: "rf_duration_x", confidence_note: "ok",
    });
    render(<PredictionPage />);
    fireEvent.submit(screen.getByLabelText("predict-form"));
    await waitFor(() => expect(screen.getByText(/55.4 minutes/)).toBeInTheDocument());
  });
});
