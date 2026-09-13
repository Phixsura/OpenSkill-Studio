import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "o-1" }),
}));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import MembersPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/members/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const MEMBERS = [
  {
    id: "m-1",
    role: "owner",
    status: "active",
    joined_at: "2026-01-01T00:00:00Z",
    user: { id: "u-1", email: "a@x.com", display_name: "Alice", avatar_url: null },
  },
  {
    id: "m-2",
    role: "student",
    status: "active",
    joined_at: "2026-02-01T00:00:00Z",
    user: { id: "u-2", email: "b@x.com", display_name: "", avatar_url: null },
  },
];

function route(posts: { path: string; body: unknown }[], opts?: { total?: number }) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method === "POST") {
      posts.push({ path, body: JSON.parse(init.body ?? "{}") });
      return Promise.resolve({ data: { code: "INV123" } });
    }
    return Promise.resolve({ data: MEMBERS, meta: { total: opts?.total ?? 2 } });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("OrgMembersPage (R420)", () => {
  it("member rows: avatar initial, Unknown fallback for empty display name, role chips, total", async () => {
    route([]);
    render(<MembersPage />, { wrapper: wrapper() });
    await screen.findByText("Alice");
    const body = document.body.textContent ?? "";
    expect(body).toContain("2 members");
    expect(screen.getByText("A")).toBeTruthy(); // Alice's initial
    expect(screen.getByText("Unknown")).toBeTruthy(); // empty display_name
    expect(screen.getByText("?")).toBeTruthy(); // fallback initial
    expect(body).toContain("a@x.com");
    // no truncation note when all rows are shown
    expect(screen.queryByText(/Showing .* of .* members/)).toBeNull();
  });

  it("invite flow: generates a /join/{code} link with the SELECTED role in the POST body", async () => {
    const posts: { path: string; body: unknown }[] = [];
    route(posts);
    render(<MembersPage />, { wrapper: wrapper() });
    await screen.findByText("Alice");
    fireEvent.click(screen.getByRole("button", { name: "Invite" }));
    fireEvent.change(screen.getByDisplayValue("Student"), { target: { value: "instructor" } });
    fireEvent.click(screen.getByRole("button", { name: "Generate Link" }));
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0]?.path).toBe("/orgs/o-1/invite-links");
    expect(posts[0]?.body).toEqual({ role: "instructor", max_uses: 10 });
    const linkInput = (await screen.findByDisplayValue(/\/join\/INV123$/)) as HTMLInputElement;
    expect(linkInput.readOnly).toBe(true);
  });

  it("invite failure clears any prior link and toasts the error", async () => {
    const posts: { path: string; body: unknown }[] = [];
    route(posts);
    render(<MembersPage />, { wrapper: wrapper() });
    await screen.findByText("Alice");
    fireEvent.click(screen.getByRole("button", { name: "Invite" }));
    fireEvent.click(screen.getByRole("button", { name: "Generate Link" }));
    await screen.findByDisplayValue(/\/join\/INV123$/);
    api.mockImplementation(((rawPath: unknown, init?: { method?: string }) => {
      if (init?.method === "POST") return Promise.reject(new Error("Invites disabled"));
      return Promise.resolve({ data: MEMBERS, meta: { total: 2 } });
    }) as typeof apiWithAuth);
    fireEvent.click(screen.getByRole("button", { name: "Generate Link" }));
    await waitFor(() => expect(toasts.error).toHaveBeenCalledWith("Invites disabled"));
    expect(screen.queryByDisplayValue(/\/join\//)).toBeNull(); // stale link cleared
  });

  it("truncation note appears when the page shows fewer than total; errors surface", async () => {
    route([], { total: 50 });
    render(<MembersPage />, { wrapper: wrapper() });
    await screen.findByText("Alice");
    expect(screen.getByText("Showing 2 of 50 members")).toBeTruthy();

    vi.clearAllMocks();
    api.mockRejectedValue(new Error("members down"));
    render(<MembersPage />, { wrapper: wrapper() });
    expect(await screen.findByText("Failed to load members. Please try again.")).toBeTruthy();
  });
});
