// R69: SSO landing page — fragment consumption, hash scrub, store hydration.
import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace, push: vi.fn() }),
}));
vi.mock("@/lib/api", () => ({
  api: vi.fn(),
  ApiError: class extends Error {},
}));

const setAuth = vi.fn();
vi.mock("@/stores/auth", () => ({
  useAuthStore: (sel: (s: { setAuth: typeof setAuth }) => unknown) => sel({ setAuth }),
}));

import SsoCompletePage from "@/app/(auth)/sso-complete/page";
import { api } from "@/lib/api";

const mockApi = vi.mocked(api);

describe("sso-complete", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("consumes the fragment, scrubs the hash and hydrates the session", async () => {
    window.location.hash = "#access_token=AT1&refresh_token=RT1";
    const scrub = vi.spyOn(window.history, "replaceState");
    mockApi.mockResolvedValueOnce({ data: { id: "u1", email: "a@b.io" } });
    render(<SsoCompletePage />);
    await waitFor(() =>
      expect(mockApi).toHaveBeenCalledWith("/auth/me", {
        headers: { Authorization: "Bearer AT1" },
      }),
    );
    await waitFor(() => expect(setAuth).toHaveBeenCalledWith("AT1", { id: "u1", email: "a@b.io" }));
    expect(scrub).toHaveBeenCalled();
    expect(replace).toHaveBeenCalledWith("/dashboard");
  });

  it("shows an error when the fragment is missing", async () => {
    window.location.hash = "";
    render(<SsoCompletePage />);
    await waitFor(() => expect(screen.getByRole("alert").textContent).toMatch(/incomplete/));
    expect(mockApi).not.toHaveBeenCalled();
  });
});
