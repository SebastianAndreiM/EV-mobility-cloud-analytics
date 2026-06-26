import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../hooks/useAuth";
import LoginPage from "../pages/LoginPage";
import * as authApi from "../api/authApi";

vi.mock("../api/authApi");

function renderPage() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <LoginPage />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe("LoginPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders the login form", () => {
    renderPage();
    expect(screen.getByLabelText("login-form")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
  });

  it("submits credentials", async () => {
    vi.mocked(authApi.login).mockResolvedValue("fake-token");
    vi.mocked(authApi.getMe).mockResolvedValue({
      id: 1, email: "a@b.com", full_name: null, created_at: "now",
    });
    renderPage();
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "a@b.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "secret123" } });
    fireEvent.submit(screen.getByLabelText("login-form"));
    await waitFor(() => expect(authApi.login).toHaveBeenCalledWith("a@b.com", "secret123"));
  });
});
