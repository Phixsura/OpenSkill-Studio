import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const nav = vi.hoisted(() => ({ token: null as string | null }));
vi.mock("next/navigation", () => ({
  useSearchParams: () => ({ get: (k: string) => (k === "token" ? nav.token : null) }),
}));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
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

import ForgotPasswordPage from "@/app/(auth)/forgot-password/page";
import ResetPasswordPage from "@/app/(auth)/reset-password/page";
import { api, ApiError } from "@/lib/api";

const apiMock = vi.mocked(api);

beforeEach(() => {
  vi.clearAllMocks();
  nav.token = "tok-1";
});

describe("ForgotPasswordPage (R481)", () => {
  it("shows the check-email screen on success AND on failure (no user-existence oracle)", async () => {
    apiMock.mockResolvedValue({});
    const first = render(<ForgotPasswordPage />);
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "ada@x.com" } });
    fireEvent.click(screen.getByRole("button", { name: "Send reset link" }));
    await screen.findByText("Check your email");
    expect(apiMock).toHaveBeenCalledWith("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email: "ada@x.com" }),
    });
    first.unmount();

    // API rejection (e.g. unknown email) must render the SAME screen
    vi.clearAllMocks();
    apiMock.mockRejectedValue(new ApiError(404, "NOT_FOUND", "no such user"));
    render(<ForgotPasswordPage />);
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "ghost@x.com" } });
    fireEvent.click(screen.getByRole("button", { name: "Send reset link" }));
    await screen.findByText("Check your email");
    expect(document.body.textContent).not.toContain("no such user");
  });
});

describe("ResetPasswordPage (R481)", () => {
  function fill(pw: string, confirm: string) {
    fireEvent.change(screen.getByLabelText("New password"), { target: { value: pw } });
    fireEvent.change(screen.getByLabelText("Confirm password"), { target: { value: confirm } });
    fireEvent.click(screen.getByRole("button", { name: "Reset password" }));
  }

  it("missing token shows the invalid-link screen without a form", () => {
    nav.token = null;
    render(<ResetPasswordPage />);
    expect(screen.getByText("Invalid link")).toBeTruthy();
    expect(screen.queryByLabelText("New password")).toBeNull();
    expect(screen.getByText("Request a new reset link").closest("a")?.getAttribute("href")).toBe(
      "/forgot-password",
    );
  });

  it("client ladder: length, uppercase, digit, then MISMATCH — all block the API call", async () => {
    render(<ResetPasswordPage />);
    fill("Ab1", "Ab1");
    expect(await screen.findByText("Password must be at least 8 characters.")).toBeTruthy();
    fill("abcdefg1", "abcdefg1");
    expect(
      await screen.findByText("Password must contain at least one uppercase letter."),
    ).toBeTruthy();
    fill("Abcdefgh", "Abcdefgh");
    expect(await screen.findByText("Password must contain at least one digit.")).toBeTruthy();
    fill("Abcdefg1", "Abcdefg2");
    expect(await screen.findByText("Passwords do not match.")).toBeTruthy();
    expect(apiMock).not.toHaveBeenCalled();
  });

  it("valid submit posts token + new_password and shows success with a login link", async () => {
    apiMock.mockResolvedValue({});
    render(<ResetPasswordPage />);
    fill("Abcdefg1", "Abcdefg1");
    await screen.findByText("Password reset");
    expect(apiMock).toHaveBeenCalledWith("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify({ token: "tok-1", new_password: "Abcdefg1" }),
    });
    expect(screen.getByText("Log in").closest("a")?.getAttribute("href")).toBe("/login");
  });

  it("ApiError verbatim; generic expired-link fallback otherwise", async () => {
    apiMock.mockRejectedValue(new ApiError(400, "TOKEN_USED", "Reset link already used"));
    const first = render(<ResetPasswordPage />);
    fill("Abcdefg1", "Abcdefg1");
    expect(await screen.findByText("Reset link already used")).toBeTruthy();
    first.unmount();

    vi.clearAllMocks();
    apiMock.mockRejectedValue(new Error("boom"));
    render(<ResetPasswordPage />);
    fill("Abcdefg1", "Abcdefg1");
    await waitFor(() => expect(document.body.textContent).toContain("Failed to reset password"));
  });
});
