import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const nav = vi.hoisted(() => ({ push: vi.fn() }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push: nav.push }) }));
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

import ClientAccessPage from "@/app/client/access/page";
import { api, ApiError } from "@/lib/api";

const apiMock = vi.mocked(api);

const SESSION = {
  access_token: "guest-jwt",
  token_type: "bearer",
  project: { id: "p-9", title: "Campaign" },
  role: "commenter",
  label: "Client X",
  expires_in: 1800,
};

function submit(code: string, email?: string) {
  fireEvent.change(screen.getByPlaceholderText("Access code"), { target: { value: code } });
  if (email !== undefined)
    fireEvent.change(screen.getByPlaceholderText(/Your email/), { target: { value: email } });
  fireEvent.click(screen.getByRole("button", { name: /Open project/ }));
}

beforeEach(() => {
  vi.clearAllMocks();
  sessionStorage.clear();
});

describe("ClientAccessPage (R480)", () => {
  it("valid code stores the guest JWT in sessionStorage (never localStorage) and routes to the project", async () => {
    apiMock.mockResolvedValue({ data: SESSION });
    render(<ClientAccessPage />);
    // button disabled until a code is typed
    expect(
      (screen.getByRole("button", { name: /Open project/ }) as HTMLButtonElement).disabled,
    ).toBe(true);
    submit("CODE123");
    await waitFor(() => expect(nav.push).toHaveBeenCalledWith("/client/p-9"));
    expect(apiMock).toHaveBeenCalledWith("/client-portal/guest-session", {
      method: "POST",
      body: JSON.stringify({ token: "CODE123" }), // no email key when blank
    });
    expect(sessionStorage.getItem("client_portal_jwt")).toBe("guest-jwt");
    expect(sessionStorage.getItem("client_portal_role")).toBe("commenter");
    expect(sessionStorage.getItem("client_portal_label")).toBe("Client X");
    expect(localStorage.getItem("client_portal_jwt")).toBeNull(); // session-scoped only
  });

  it("email included in the body only when provided", async () => {
    apiMock.mockResolvedValue({ data: SESSION });
    render(<ClientAccessPage />);
    submit("CODE123", "client@x.com");
    await waitFor(() => expect(apiMock).toHaveBeenCalled());
    expect(JSON.parse((apiMock.mock.calls[0]?.[1] as { body: string }).body)).toEqual({
      token: "CODE123",
      email: "client@x.com",
    });
  });

  it("status-specific errors: 401 expired-link, 429 rate-limit, 422 verbatim message, generic fallback", async () => {
    const cases: [Error, RegExp][] = [
      [new ApiError(401, "INVALID", "x"), /invalid or has expired/],
      [new ApiError(429, "RATE", "x"), /Too many attempts/],
      [new ApiError(422, "MALFORMED", "Code must be 12 chars"), /Code must be 12 chars/],
      [new Error("network"), /Something went wrong/],
    ];
    for (const [err, expected] of cases) {
      apiMock.mockRejectedValue(err);
      const view = render(<ClientAccessPage />);
      submit("CODE123");
      await waitFor(() => expect(document.body.textContent, String(err)).toMatch(expected));
      expect(nav.push).not.toHaveBeenCalled();
      view.unmount();
      vi.clearAllMocks();
    }
  });
});
