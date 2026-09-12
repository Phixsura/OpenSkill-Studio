import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const nav = vi.hoisted(() => ({
  push: vi.fn(),
  replace: vi.fn(),
  redirectParam: null as string | null,
}));
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: nav.push, replace: nav.replace }),
  useSearchParams: () => ({ get: (k: string) => (k === "redirect" ? nav.redirectParam : null) }),
}));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
const auth = vi.hoisted(() => ({
  state: { isAuthenticated: false, setAuth: vi.fn() } as {
    isAuthenticated: boolean;
    setAuth: (t: string, u: unknown) => void;
  },
}));
vi.mock("@/stores/auth", () => ({
  useAuthStore: (sel: (s: typeof auth.state) => unknown) => sel(auth.state),
}));
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
  return { api: vi.fn(), ApiError: MockApiError };
});

import RegisterPage from "@/app/(auth)/register/page";
import { api, ApiError } from "@/lib/api";

const apiMock = vi.mocked(api);

function fill(pw: string) {
  fireEvent.change(screen.getByLabelText("Name"), { target: { value: "Ada" } });
  fireEvent.change(screen.getByLabelText("Email"), { target: { value: "ada@x.com" } });
  fireEvent.change(screen.getByLabelText("Password"), { target: { value: pw } });
  fireEvent.click(screen.getByRole("button", { name: "Sign up" }));
}

beforeEach(() => {
  vi.clearAllMocks();
  auth.state = { isAuthenticated: false, setAuth: vi.fn() };
  nav.redirectParam = null;
});

describe("RegisterPage (R476)", () => {
  it("client password ladder blocks the API call: length, uppercase, digit", async () => {
    const { unmount } = render(<RegisterPage />);
    fill("Ab1");
    expect(await screen.findByText("Password must be at least 8 characters.")).toBeTruthy();
    fill("abcdefg1");
    expect(
      await screen.findByText("Password must contain at least one uppercase letter."),
    ).toBeTruthy();
    fill("Abcdefgh");
    expect(await screen.findByText("Password must contain at least one digit.")).toBeTruthy();
    expect(apiMock).not.toHaveBeenCalled(); // no round-trip on client-side failure
    unmount();
  });

  it("valid submit posts credentials, stores auth, shows verify screen; Continue uses safeRedirect", async () => {
    apiMock.mockResolvedValue({
      access_token: "tok",
      token_type: "bearer",
      expires_in: 900,
      user: { id: "u-1" },
    });
    nav.redirectParam = "/join/INV123";
    render(<RegisterPage />);
    fill("Abcdefg1");
    await screen.findByText("Check your email");
    expect(apiMock).toHaveBeenCalledWith("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email: "ada@x.com", password: "Abcdefg1", display_name: "Ada" }),
      credentials: "include",
    });
    expect(auth.state.setAuth).toHaveBeenCalledWith("tok", { id: "u-1" });
    expect(document.body.textContent).toContain("ada@x.com"); // email echoed
    fireEvent.click(screen.getByRole("button", { name: "Continue to Dashboard" }));
    expect(nav.push).toHaveBeenCalledWith("/join/INV123"); // safe relative target honored
  });

  it("open-redirect targets fall back to /dashboard on Continue", async () => {
    for (const evil of [
      "//evil.com",
      "/\\evil.com",
      "/%09/evil.com".replace("%09", "\t"),
      "https://evil.com",
    ]) {
      apiMock.mockResolvedValue({
        access_token: "tok",
        token_type: "bearer",
        expires_in: 900,
        user: { id: "u-1" },
      });
      nav.redirectParam = evil;
      const view = render(<RegisterPage />);
      fill("Abcdefg1");
      await screen.findByText("Check your email");
      fireEvent.click(screen.getByRole("button", { name: "Continue to Dashboard" }));
      expect(nav.push, `target: ${JSON.stringify(evil)}`).toHaveBeenCalledWith("/dashboard");
      view.unmount();
      vi.clearAllMocks();
      auth.state = { isAuthenticated: false, setAuth: vi.fn() };
    }
  });

  it("already-authenticated users are bounced to /dashboard UNLESS an invite redirect is present", async () => {
    auth.state = { isAuthenticated: true, setAuth: vi.fn() };
    const first = render(<RegisterPage />);
    await waitFor(() => expect(nav.replace).toHaveBeenCalledWith("/dashboard"));
    first.unmount();

    vi.clearAllMocks();
    nav.redirectParam = "/join/INV123";
    render(<RegisterPage />);
    await screen.findByText("Create an account");
    expect(nav.replace).not.toHaveBeenCalled(); // invite flow stays on the form
  });

  it("ApiError shown verbatim, generic fallback otherwise", async () => {
    apiMock.mockRejectedValue(new ApiError(409, "EMAIL_TAKEN", "Email already registered"));
    const first = render(<RegisterPage />);
    fill("Abcdefg1");
    expect(await screen.findByText("Email already registered")).toBeTruthy();
    first.unmount();

    vi.clearAllMocks();
    apiMock.mockRejectedValue(new Error("boom"));
    render(<RegisterPage />);
    fill("Abcdefg1");
    expect(await screen.findByText(/Registration failed/)).toBeTruthy();
  });
});
