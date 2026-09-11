import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
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

import PlatformPartnersPage from "@/app/(dashboard)/platform/partners/page";
import PlatformTenantsPage from "@/app/(dashboard)/platform/tenants/page";
import { apiWithAuth, ApiError } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

beforeEach(() => vi.clearAllMocks());

const TENANT = {
  id: "t-1",
  name: "North School",
  slug: "north",
  status: "active",
  account_type: "direct",
  currency: "USD",
  partner_id: null,
  created_at: "2026-08-01T00:00:00Z",
};

describe("PlatformTenantsPage (R413)", () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it("debounced q + status filter land in the request and reset paging; row links to detail", async () => {
    const calls: string[] = [];
    api.mockImplementation((rawPath: unknown) => {
      calls.push(String(rawPath ?? ""));
      return Promise.resolve({ data: [TENANT], meta: { has_more: true } });
    });
    render(<PlatformTenantsPage />, { wrapper: wrapper() });
    await vi.advanceTimersByTimeAsync(450);
    await vi.waitFor(() => expect(screen.getByText("North School")).toBeTruthy());
    expect(screen.getByText("North School").closest("a")?.getAttribute("href")).toBe(
      "/platform/tenants/t-1",
    );
    // page 2, then a status change must reset to page 1 immediately
    fireEvent.click(screen.getByRole("button", { name: /next/i }));
    await vi.waitFor(() => expect(calls.some((c) => c.includes("page=2"))).toBe(true));
    fireEvent.change(screen.getByDisplayValue("all statuses"), {
      target: { value: "suspended" },
    });
    await vi.waitFor(() => {
      const last = calls[calls.length - 1];
      expect(last).toContain("status=suspended");
      expect(last).toContain("page=1");
    });
    // typed search is debounced: nothing inside the window, then one request
    const before = calls.length;
    fireEvent.change(screen.getByPlaceholderText("Search name / slug / billing email"), {
      target: { value: "north" },
    });
    await vi.advanceTimersByTimeAsync(200);
    expect(calls.length).toBe(before);
    await vi.advanceTimersByTimeAsync(300);
    await vi.waitFor(() => {
      expect(calls[calls.length - 1]).toContain("q=north");
    });
  });

  it("query errors surface via QueryError", async () => {
    api.mockImplementation(() => Promise.reject(new Error("fleet down")));
    render(<PlatformTenantsPage />, { wrapper: wrapper() });
    await vi.advanceTimersByTimeAsync(450);
    await vi.waitFor(() => {
      expect(document.body.textContent).toMatch(/tenants/i);
      expect(document.body.textContent).toMatch(/failed|error|down/i);
    });
  });
});

describe("PlatformPartnersPage (R413)", () => {
  it("create flow posts name/slug/type, closes the form, and clears fields on success", async () => {
    const posts: { path: string; body: unknown }[] = [];
    api.mockImplementation((rawPath: unknown, init?: { method?: string; body?: string }) => {
      const path = String(rawPath ?? "");
      if (init?.method === "POST") {
        posts.push({ path, body: JSON.parse(init.body ?? "{}") });
        return Promise.resolve({ data: { id: "pt-9" } });
      }
      return Promise.resolve({ data: [], meta: { has_more: false } });
    });
    render(<PlatformPartnersPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByRole("button", { name: "New partner" }));
    // Create is disabled until BOTH name and slug are set
    const create = screen.getByRole("button", { name: "Create" }) as HTMLButtonElement;
    expect(create.disabled).toBe(true);
    fireEvent.change(screen.getByPlaceholderText("Name"), { target: { value: "Acme" } });
    expect(create.disabled).toBe(true);
    fireEvent.change(screen.getByPlaceholderText("slug"), { target: { value: "acme" } });
    fireEvent.change(screen.getByDisplayValue("reseller"), {
      target: { value: "school_channel" },
    });
    expect(create.disabled).toBe(false);
    fireEvent.click(create);
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0].path).toBe("/platform/partners");
    expect(posts[0].body).toEqual({ name: "Acme", slug: "acme", partner_type: "school_channel" });
    await waitFor(() => expect(toasts.success).toHaveBeenCalledWith("Partner created"));
    // form closed after success
    expect(screen.queryByPlaceholderText("Name")).toBeNull();
  });

  it("create failure surfaces the API error message in a toast", async () => {
    api.mockImplementation((rawPath: unknown, init?: { method?: string }) => {
      if (init?.method === "POST")
        return Promise.reject(
          new (ApiError as new (s: number, c: string, m: string) => Error)(
            409,
            "SLUG_TAKEN",
            "Slug already in use",
          ),
        );
      return Promise.resolve({ data: [], meta: { has_more: false } });
    });
    render(<PlatformPartnersPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByRole("button", { name: "New partner" }));
    fireEvent.change(screen.getByPlaceholderText("Name"), { target: { value: "Acme" } });
    fireEvent.change(screen.getByPlaceholderText("slug"), { target: { value: "acme" } });
    fireEvent.click(screen.getByRole("button", { name: "Create" }));
    await waitFor(() => expect(toasts.error).toHaveBeenCalledWith("Slug already in use"));
    // form stays open with the typed values preserved for correction
    expect((screen.getByPlaceholderText("Name") as HTMLInputElement).value).toBe("Acme");
  });
});
