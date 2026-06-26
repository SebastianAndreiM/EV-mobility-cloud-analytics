import { createContext, useContext, useState, ReactNode, useCallback } from "react";
import { setAuthToken } from "../api/client";
import * as authApi from "../api/authApi";
import type { User } from "../api/authApi";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  // Token kept in memory only (no localStorage) per design choice.
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);

  const login = useCallback(async (email: string, password: string) => {
    const accessToken = await authApi.login(email, password);
    setAuthToken(accessToken);
    setToken(accessToken);
    const me = await authApi.getMe();
    setUser(me);
  }, []);

  const register = useCallback(
    async (email: string, password: string, fullName?: string) => {
      await authApi.register(email, password, fullName);
      await login(email, password);
    },
    [login]
  );

  const logout = useCallback(() => {
    setAuthToken(null);
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, token, isAuthenticated: !!token, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
