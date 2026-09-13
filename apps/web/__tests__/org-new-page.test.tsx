import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const nav = vi.hoisted(() => ({ replace: vi.fn() }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace: nav.replace }) }));
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

import CreateOrgPage from "@/app/(dashboard)/dashboard/orgs/new/page";
import { apiWithAuth, ApiError } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function body(call: unknown[]) {
  return JSON.parse((call[1] as { body: string }).body);
}

beforeEach(() => vi.clearAllMocks());

describe("CreateOrgPage (R477)", () => {
  it("auto-slug is derived from the name (lowercased, punctuation collapsed, trimmed) and shown as placeholder", async () => {
    api.mockResolvedValue({ data: { id: "org-9" } });
    render(<CreateOrgPage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByLabelText("Organization name"), {
      target: { value: "  AI Creators!! Academy  " },
    });
    expect(screen.getByLabelText("URL slug").getAttribute("placeholder")).toBe(
      "ai-creators-academy",
    );
    fireEvent.click(screen.getByRole("button", { name: "Create Organization" }));
    await waitFor(() => expect(api).toHaveBeenCalled());
    // empty slug + empty description -> auto slug sent, description omitted
    expect(body(api.mock.calls[0] as unknown[])).toEqual({
      name: "  AI Creators!! Academy  ",
      slug: "ai-creators-academy",
    });
    expect(nav.replace).toHaveBeenCalledWith("/dashboard/orgs/org-9");
  });

  it("explicit slug wins over auto-slug; description included when set", async () => {
    api.mockResolvedValue({ data: { id: "org-9" } });
    render(<CreateOrgPage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByLabelText("Organization name"), { target: { value: "My Org" } });
    fireEvent.change(screen.getByLabelText("URL slug"), { target: { value: "custom-slug" } });
    fireEvent.change(screen.getByLabelText("Description"), { target: { value: "About us" } });
    fireEvent.click(screen.getByRole("button", { name: "Create Organization" }));
    await waitFor(() => expect(api).toHaveBeenCalled());
    expect(body(api.mock.calls[0] as unknown[])).toEqual({
      name: "My Org",
      slug: "custom-slug",
      description: "About us",
    });
  });

  it("double-submit guard: a second click while in flight posts once", async () => {
    let resolve!: (v: unknown) => void;
    api.mockImplementation(
      (() => new Promise((r) => (resolve = r))) as unknown as typeof apiWithAuth,
    );
    render(<CreateOrgPage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByLabelText("Organization name"), { target: { value: "My Org" } });
    const btn = screen.getByRole("button", { name: "Create Organization" });
    fireEvent.click(btn);
    fireEvent.click(btn); // second click mid-flight
    fireEvent.submit(btn.closest("form") as HTMLFormElement); // even a raw re-submit
    resolve({ data: { id: "org-9" } });
    await waitFor(() => expect(nav.replace).toHaveBeenCalled());
    expect(api).toHaveBeenCalledTimes(1);
  });

  it("ApiError verbatim vs generic fallback; form stays usable after failure", async () => {
    api.mockRejectedValue(new ApiError(409, "SLUG_TAKEN", "Slug already taken"));
    const first = render(<CreateOrgPage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByLabelText("Organization name"), { target: { value: "My Org" } });
    fireEvent.click(screen.getByRole("button", { name: "Create Organization" }));
    expect(await screen.findByText("Slug already taken")).toBeTruthy();
    expect(nav.replace).not.toHaveBeenCalled();
    // retry after failure is allowed (submitting ref released)
    api.mockResolvedValue({ data: { id: "org-9" } });
    fireEvent.click(screen.getByRole("button", { name: "Create Organization" }));
    await waitFor(() => expect(nav.replace).toHaveBeenCalledWith("/dashboard/orgs/org-9"));
    first.unmount();

    vi.clearAllMocks();
    api.mockRejectedValue(new Error("boom"));
    render(<CreateOrgPage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByLabelText("Organization name"), { target: { value: "My Org" } });
    fireEvent.click(screen.getByRole("button", { name: "Create Organization" }));
    expect(await screen.findByText("Failed to create organization.")).toBeTruthy();
  });
});
