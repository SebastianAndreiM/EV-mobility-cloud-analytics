import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "../hooks/useAuth";
import ProtectedRoute from "../components/ProtectedRoute";

describe("ProtectedRoute", () => {
  it("redirects unauthenticated users to /login", () => {
    render(
      <MemoryRouter initialEntries={["/secret"]}>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<div>Login Screen</div>} />
            <Route path="/secret" element={
              <ProtectedRoute><div>Secret</div></ProtectedRoute>
            } />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );
    expect(screen.getByText("Login Screen")).toBeInTheDocument();
    expect(screen.queryByText("Secret")).not.toBeInTheDocument();
  });
});
