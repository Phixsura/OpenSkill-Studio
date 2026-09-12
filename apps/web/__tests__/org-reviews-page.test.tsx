import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1" }) }));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import ReviewDashboardPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/reviews/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const SUBS = [
  {
    id: "s-1",
    project_id: "p-1",
    user_id: "u-1",
    version: 2,
    status: "submitted",
    submitted_at: "2026-09-01T10:00:00Z",
    is_late: true,
    author_name: "Ada",
    project_title: "Chatbot",
  },
  {
    id: "s-2",
    project_id: "p-2",
    user_id: "u-2",
    version: 1,
    status: "submitted",
    submitted_at: "2026-09-02T10:00:00Z",
    is_late: false,
    author_name: "bob",
    project_title: "Pipeline",
  },
];

function route(subs: unknown[], meta: Record<string, unknown>, capture?: string[]) {
  api.mockImplementation((rawPath: unknown) => {
    capture?.push(String(rawPath ?? ""));
    return Promise.resolve({ data: subs, meta });
  });
}

beforeEach(() => vi.clearAllMocks());

describe("ReviewDashboardPage (R451)", () => {
  it("rows: late/on-time status, version, avatar initial, review link", async () => {
    route(SUBS, { total: 2, has_more: false });
    render(<ReviewDashboardPage />, { wrapper: wrapper() });
    await screen.findByText("Chatbot");
    const body = document.body.textContent ?? "";
    expect(body).toContain("2 submissions awaiting review."); // plural
    expect(screen.getByText("Late").className).toContain("text-yellow-600");
    expect(screen.getByText("On time").className).toContain("text-green-600");
    expect(body).toContain("v2");
    // avatar initial is the author name's first char
    expect(screen.getByText("A")).toBeTruthy(); // Ada -> A
    // review link points at the submission
    expect(screen.getAllByText("Review →")[0].closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/reviews/s-1",
    );
  });

  it("singular count copy and empty state", async () => {
    route([], { total: 0, has_more: false });
    render(<ReviewDashboardPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/No pending reviews/)).toBeTruthy();
    // exactly-1 uses the singular noun
    vi.clearAllMocks();
    route([SUBS[0]], { total: 1, has_more: false });
    render(<ReviewDashboardPage />, { wrapper: wrapper() });
    await screen.findByText("Chatbot");
    expect(document.body.textContent).toContain("1 submission awaiting review.");
  });

  it("pager sends the page and shows the range; Next disabled without has_more", async () => {
    const calls: string[] = [];
    route(SUBS, { total: 40, has_more: true }, calls);
    const first = render(<ReviewDashboardPage />, { wrapper: wrapper() });
    await screen.findByText("Chatbot");
    expect(document.body.textContent).toContain("Showing 1–20 of 40");
    fireEvent.click(screen.getByRole("button", { name: "Next" }));
    await waitFor(() => expect(calls.some((c) => c.includes("page=2"))).toBe(true));
    first.unmount();

    vi.clearAllMocks();
    route(SUBS, { total: 2, has_more: false });
    render(<ReviewDashboardPage />, { wrapper: wrapper() });
    await screen.findByText("Chatbot");
    // total <= perPage and page 1 → no pager
    expect(screen.queryByRole("button", { name: "Next" })).toBeNull();
  });

  it("fetch error surfaces the retry line", async () => {
    api.mockImplementation(() => Promise.reject(new Error("reviews down")));
    render(<ReviewDashboardPage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toMatch(/Failed to load reviews/));
  });
});
