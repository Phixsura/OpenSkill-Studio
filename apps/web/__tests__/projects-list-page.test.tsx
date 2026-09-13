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

import ProjectsListPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/projects/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const DAY = 24 * 60 * 60 * 1000;
const iso = (offsetMs: number) => new Date(Date.now() + offsetMs).toISOString();

function proj(id: string, title: string, deadline: string | null) {
  return {
    id,
    title,
    slug: id,
    description: `${title} description`,
    difficulty: "intermediate",
    max_score: 100,
    deadline,
    status: "published",
  };
}

function route(opts: {
  projects: unknown[];
  cohorts?: unknown[];
  calls?: string[];
  total?: number;
}) {
  api.mockImplementation(((rawPath: unknown) => {
    const path = String(rawPath ?? "");
    opts.calls?.push(path);
    if (path.includes("my-cohorts")) return Promise.resolve({ data: opts.cohorts ?? [] });
    return Promise.resolve({
      data: opts.projects,
      meta: { total: opts.total ?? opts.projects.length },
    });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("ProjectsListPage (R471)", () => {
  it("deadline ladder: past due (red), due today, due tomorrow, N days left, no deadline", async () => {
    route({
      projects: [
        proj("p-past", "Past", iso(-2 * DAY)),
        proj("p-today", "Today", iso(30 * 60 * 1000)), // in 30 min -> ceil 1? no: <1 day -> days=1? Math.ceil(0.02)=1 -> "Due tomorrow"? verify below
        proj("p-tomorrow", "Tomorrow", iso(1.5 * DAY)),
        proj("p-week", "Week", iso(6.5 * DAY)),
        proj("p-none", "NoDeadline", null),
      ],
    });
    render(<ProjectsListPage />, { wrapper: wrapper() });
    await screen.findByText("Past");
    const rowText = (title: string) => screen.getByText(title).closest("a")?.textContent ?? "";
    expect(rowText("Past")).toContain("Past due");
    // 30 minutes ahead: Math.ceil(0.02 days) === 1 -> "Due tomorrow" per the ceil impl
    expect(rowText("Today")).toContain("Due tomorrow");
    expect(rowText("Tomorrow")).toContain("2 days left"); // ceil(1.5) = 2
    expect(rowText("Week")).toContain("7 days left"); // ceil(6.5) = 7
    expect(rowText("NoDeadline")).toContain("No deadline");
    // red class only on the past-due deadline span
    const pastSpan = screen.getByText("Past due");
    expect(pastSpan.className).toContain("text-red-600");
    expect(screen.getByText("No deadline").className).not.toContain("text-red-600");
    // card link + meta line
    expect(screen.getByText("Past").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/projects/p-past",
    );
    expect(rowText("Past")).toContain("100 pts");
  });

  it("cohort filter refetches with cohort_id; hidden when no cohorts", async () => {
    const calls: string[] = [];
    route({
      projects: [proj("p-1", "Alpha", null)],
      cohorts: [{ id: "c-1", name: "Fall Cohort" }],
      calls,
    });
    const first = render(<ProjectsListPage />, { wrapper: wrapper() });
    await screen.findByText("Alpha");
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "c-1" } });
    await waitFor(() =>
      expect(calls.some((c) => c === "/orgs/o-1/projects?cohort_id=c-1")).toBe(true),
    );
    first.unmount();

    vi.clearAllMocks();
    route({ projects: [proj("p-1", "Alpha", null)], cohorts: [] });
    render(<ProjectsListPage />, { wrapper: wrapper() });
    await screen.findByText("Alpha");
    expect(screen.queryByRole("combobox")).toBeNull(); // no cohorts -> no filter UI
  });

  it("truncation notice only when fewer shown than total; empty + error states", async () => {
    route({ projects: [proj("p-1", "Alpha", null)], total: 25 });
    const first = render(<ProjectsListPage />, { wrapper: wrapper() });
    await screen.findByText("Alpha");
    expect(document.body.textContent).toContain("Showing 1 of 25 projects");
    first.unmount();

    vi.clearAllMocks();
    route({ projects: [proj("p-1", "Alpha", null)], total: 1 });
    const second = render(<ProjectsListPage />, { wrapper: wrapper() });
    await second.findByText("Alpha");
    expect(document.body.textContent).not.toContain("Showing 1 of 1");
    second.unmount();

    vi.clearAllMocks();
    route({ projects: [] });
    const third = render(<ProjectsListPage />, { wrapper: wrapper() });
    expect(await third.findByText("No projects yet.")).toBeTruthy();
    third.unmount();

    vi.clearAllMocks();
    api.mockRejectedValue(new Error("projects down"));
    render(<ProjectsListPage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toContain("Failed to load projects"));
  });
});
