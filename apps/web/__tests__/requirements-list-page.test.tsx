import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1" }) }));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import RequirementsPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/requirements/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const PROFILES = [
  {
    id: "p-1",
    context_type: "learning",
    raw_request: null,
    status: "confirmed",
    structured_requirements: { goal: "Learn compositing" },
    created_at: "2026-09-01T00:00:00Z",
  },
  {
    id: "p-2",
    context_type: "production",
    raw_request: "raw text here",
    status: "draft",
    structured_requirements: {},
    created_at: "2026-09-02T00:00:00Z",
  },
  {
    id: "p-3",
    context_type: "production",
    raw_request: null,
    status: "draft",
    structured_requirements: {},
    created_at: "2026-09-03T00:00:00Z",
  },
];

beforeEach(() => vi.clearAllMocks());

describe("RequirementsPage (R468)", () => {
  it("goal display falls back goal -> raw_request -> placeholder", async () => {
    api.mockResolvedValue({ data: PROFILES, meta: { total: 3, has_more: false } });
    render(<RequirementsPage />, { wrapper: wrapper() });
    await screen.findByText("Learn compositing");
    const body = document.body.textContent ?? "";
    expect(body).toContain("raw text here"); // p-2: no goal -> raw request
    expect(body).toContain("(no goal specified)"); // p-3: neither
    // status chips + humanized context type
    expect(screen.getByText("confirmed")).toBeTruthy();
    expect(body).toContain("production");
    // rows link to the profile detail
    expect(screen.getByText("Learn compositing").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/requirements/p-1",
    );
  });

  it("error state surfaces", async () => {
    api.mockRejectedValue(new Error("profiles down"));
    render(<RequirementsPage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toMatch(/Failed|error/i));
  });
});
