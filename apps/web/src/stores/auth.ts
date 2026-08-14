import { create } from "zustand";

export interface AuthUser {
  id: string;
  email: string;
  email_verified: boolean;
  display_name: string;
  avatar_url: string | null;
  role: string;
  created_at: string;
}

interface AuthState {
  accessToken: string | null;
  user: AuthUser | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: AuthUser) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  isAuthenticated: false,
  setAuth: (token, user) =>
    set({ accessToken: token, user, isAuthenticated: true }),
  clearAuth: () =>
    set({ accessToken: null, user: null, isAuthenticated: false }),
}));
