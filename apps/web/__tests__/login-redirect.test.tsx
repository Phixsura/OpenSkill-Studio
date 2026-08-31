import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";

const push = vi.fn();
let redirectParam: string | null = null;

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, replace: vi.fn() }),
  useSearchParams: () => ({
    get: (key: string) => (key === "redirect" ? redirectParam : null),
  }),
}));

vi.mock("@/lib/api", () => ({
  api: vi.fn(),
  ApiError: class extends Error {},
}));

import LoginPage from "@/app/(auth)/login/page";
import { api } from "@/lib/api";

const mockApi = vi.mocked(api);

const AUTH_RESPONSE = {
  access_token: "tok",
  token_type: "bearer",
  expires_in: 900,
  user: {
    id: "u1",
    email: "a@b.co",
    email_verified: true,
    display_name: "A",
    avatar_url: null,
    role: "user",
    created_at: "2026-01-01T00:00:00Z",
  },
};

async function loginWithRedirect(redirect: string | null): Promise<string> {
  redirectParam = redirect;
  push.mockClear();
  mockApi.mockResolvedValue(AUTH_RESPONSE);
  const { unmount } = render(<LoginPage />);
  fireEvent.change(screen.getByLabelText("Email"), {
    target: { value: "a@b.co" },
  });
  fireEvent.change(screen.getByLabelText("Password"), {
    target: { value: "Password1" },
  });
  fireEvent.click(screen.getByRole("button", { name: /log in/i }));
  await waitFor(() => expect(push).toHaveBeenCalled());
  const target = push.mock.calls[0]?.[0] as string;
  unmount();
  return target;
}

describe("LoginPage redirect guard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Fresh auth store per test — setAuth flips isAuthenticated, which
    // triggers the already-logged-in replace on the next render.
    vi.resetModules();
  });

  it("follows a safe relative redirect", async () => {
    expect(await loginWithRedirect("/dashboard/orgs/abc")).toBe("/dashboard/orgs/abc");
  });

  it("falls back to /dashboard when redirect is absent", async () => {
    expect(await loginWithRedirect(null)).toBe("/dashboard");
  });

  it("rejects protocol-relative //evil.com", async () => {
    expect(await loginWithRedirect("//evil.com")).toBe("/dashboard");
  });

  it("rejects backslash variant /\\evil.com", async () => {
    expect(await loginWithRedirect("/\\evil.com")).toBe("/dashboard");
  });

  it("rejects any backslash anywhere in the target", async () => {
    expect(await loginWithRedirect("/ok\\..\\evil")).toBe("/dashboard");
  });

  it("rejects absolute URLs", async () => {
    expect(await loginWithRedirect("https://evil.com")).toBe("/dashboard");
  });
});
