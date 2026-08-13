import { describe, it, expect, beforeEach } from "vitest";
import { useAuthStore } from "@/stores/auth";

describe("auth store", () => {
  beforeEach(() => {
    useAuthStore.getState().clearAuth();
  });

  it("should start unauthenticated", () => {
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.accessToken).toBeNull();
    expect(state.user).toBeNull();
  });

  it("should set auth state on login", () => {
    const user = {
      id: "01JK",
      email: "test@example.com",
      email_verified: false,
      display_name: "Test",
      avatar_url: null,
      role: "student",
      created_at: "2026-01-01T00:00:00Z",
    };

    useAuthStore.getState().setAuth("token123", user);

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.accessToken).toBe("token123");
    expect(state.user?.email).toBe("test@example.com");
  });

  it("should clear auth state on logout", () => {
    useAuthStore.getState().setAuth("token", {
      id: "01JK",
      email: "test@example.com",
      email_verified: false,
      display_name: "Test",
      avatar_url: null,
      role: "student",
      created_at: "2026-01-01T00:00:00Z",
    });

    useAuthStore.getState().clearAuth();

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.accessToken).toBeNull();
    expect(state.user).toBeNull();
  });
});
