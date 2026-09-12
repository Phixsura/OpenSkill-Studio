import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const push = vi.hoisted(() => vi.fn());
vi.mock("next/navigation", () => ({
  useParams: () => ({ code: "INV123" }),
  useRouter: () => ({ push }),
}));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
const auth = vi.hoisted(() => ({ state: { isAuthenticated: false } }));
vi.mock("@/stores/auth", () => {
  const useAuthStore = (sel: (s: { isAuthenticated: boolean }) => unknown) => sel(auth.state);
  useAuthStore.subscribe = () => () => {};
  return { useAuthStore };
});
vi.mock("@/lib/api", () => {
  class MockApiError extends Error {
    constructor(
      public status: number,
      public code: string,
      message: string,
    ) {
      super(message);
    }
  }
  return { apiWithAuth: vi.fn(), ApiError: MockApiError };
});

import JoinByCodePage from "@/app/join/[code]/page";
import { apiWithAuth, ApiError } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

beforeEach(() => {
  vi.clearAllMocks();
  auth.state = { isAuthenticated: false };
});
afterEach(() => vi.useRealTimers());

describe("JoinByCodePage (R475)", () => {
  it("unauthenticated: Loading for the 2s hydration grace, then login/signup with redirect back to the code", async () => {
    vi.useFakeTimers();
    render(<JoinByCodePage />);
    // during the grace window, no misleading log-in prompt
    expect(screen.getByText("Loading...")).toBeTruthy();
    expect(screen.queryByText("Log in")).toBeNull();
    act(() => vi.advanceTimersByTime(2000));
    expect(screen.getByText(/You need to log in/)).toBeTruthy();
    expect(screen.getByText("Log in").closest("a")?.getAttribute("href")).toBe(
      "/login?redirect=/join/INV123",
    );
    expect(screen.getByText("Sign up").closest("a")?.getAttribute("href")).toBe(
      "/register?redirect=/join/INV123",
    );
  });

  it("authenticated: join posts the code, shows success, redirects to the joined org after 1.5s", async () => {
    auth.state = { isAuthenticated: true };
    api.mockResolvedValue({ data: { org_id: "org-77" } });
    vi.useFakeTimers();
    render(<JoinByCodePage />);
    // authenticated -> straight to the accept screen (no grace wait)
    fireEvent.click(screen.getByRole("button", { name: "Accept & Join" }));
    await act(async () => {
      await vi.runOnlyPendingTimersAsync();
    });
    expect(screen.getByText("🎉 Welcome!")).toBeTruthy();
    expect(api).toHaveBeenCalledWith("/invites/join", {
      method: "POST",
      body: JSON.stringify({ code: "INV123" }),
    });
    expect(push).toHaveBeenCalledWith("/dashboard/orgs/org-77");
  });

  it("ApiError message shown verbatim; non-ApiError falls back to generic copy", async () => {
    auth.state = { isAuthenticated: true };
    api.mockRejectedValue(new ApiError(409, "ALREADY_MEMBER", "Already a member"));
    const first = render(<JoinByCodePage />);
    fireEvent.click(screen.getByRole("button", { name: "Accept & Join" }));
    await waitFor(() => expect(screen.getByText("Already a member")).toBeTruthy());
    expect(push).not.toHaveBeenCalled();
    first.unmount();

    vi.clearAllMocks();
    api.mockRejectedValue(new Error("network"));
    render(<JoinByCodePage />);
    fireEvent.click(screen.getByRole("button", { name: "Accept & Join" }));
    await waitFor(() => expect(screen.getByText("Failed to join.")).toBeTruthy());
  });
});
