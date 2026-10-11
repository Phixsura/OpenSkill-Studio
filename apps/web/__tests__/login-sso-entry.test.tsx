// R68 (ADR-018): the login page's enterprise-SSO entry — discovery by email
// domain, redirect to the org's authorize endpoint, graceful no-SSO message.
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  useSearchParams: () => ({ get: () => null }),
}));
vi.mock("@/lib/api", () => ({
  api: vi.fn(),
  ApiError: class extends Error {
    constructor(
      public status = 0,
      public code = "",
      message = "",
    ) {
      super(message);
    }
  },
}));
vi.mock("@/lib/useAnonExperiment", () => ({
  claimAnonymousId: vi.fn().mockResolvedValue(true),
}));

import LoginPage from "@/app/(auth)/login/page";
import { api, ApiError } from "@/lib/api";

const mockApi = vi.mocked(api);

describe("login SSO entry", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("redirects to the discovered authorize URL", async () => {
    mockApi.mockResolvedValueOnce({
      data: { sso: true, authorize_url: "/api/v1/sso/saml/authorize?connection=C1" },
    });
    const assign = vi.fn();
    Object.defineProperty(window, "location", {
      value: { ...window.location, assign },
      writable: true,
    });
    render(<LoginPage />);
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "kid@school.edu" },
    });
    fireEvent.click(screen.getByText(/Continue with single sign-on/));
    await waitFor(() => expect(mockApi).toHaveBeenCalledWith("/sso/login?email=kid%40school.edu"));
    await waitFor(() =>
      expect(assign).toHaveBeenCalledWith("/api/v1/sso/saml/authorize?connection=C1"),
    );
  });

  it("explains when the domain has no SSO, and requires an email first", async () => {
    render(<LoginPage />);
    fireEvent.click(screen.getByText(/Continue with single sign-on/));
    await waitFor(() => expect(screen.getByRole("alert").textContent).toMatch(/work email first/));
    expect(mockApi).not.toHaveBeenCalled();

    mockApi.mockResolvedValueOnce({ data: { sso: false } });
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "solo@gmail.com" },
    });
    fireEvent.click(screen.getByText(/Continue with single sign-on/));
    await waitFor(() => expect(screen.getByRole("alert").textContent).toMatch(/not configured/));
  });

  it("hands an SSO_REQUIRED password login straight into the SSO flow", async () => {
    const assign = vi.fn();
    Object.defineProperty(window, "location", {
      value: { ...window.location, assign },
      writable: true,
    });
    mockApi
      .mockRejectedValueOnce(new ApiError(403, "SSO_REQUIRED", "Use SSO"))
      .mockResolvedValueOnce({
        data: { sso: true, authorize_url: "/api/v1/sso/oidc/authorize?connection=C2" },
      });
    render(<LoginPage />);
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "emp@corp.io" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "pw" },
    });
    fireEvent.click(screen.getByText("Log in"));
    await waitFor(() =>
      expect(assign).toHaveBeenCalledWith("/api/v1/sso/oidc/authorize?connection=C2"),
    );
    expect(screen.queryByRole("alert")).toBeFalsy();
  });
});
