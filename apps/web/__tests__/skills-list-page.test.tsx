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

import SkillsListPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/skills/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const SKILLS = [
  {
    id: "s-1",
    name: "Prompting",
    slug: "prompting",
    description: "LLM prompting",
    difficulty: "beginner",
    tags: ["ai", "text"],
    status: "published",
    sort_order: 1,
  },
  {
    id: "s-2",
    name: "Compositing",
    slug: "compositing",
    description: "Video comp",
    difficulty: "expert",
    tags: [],
    status: "published",
    sort_order: 2,
  },
];

function route(calls?: string[], cohorts: unknown[] = []) {
  api.mockImplementation(((rawPath: unknown) => {
    const path = String(rawPath ?? "");
    calls?.push(path);
    if (path.includes("my-cohorts")) return Promise.resolve({ data: cohorts });
    return Promise.resolve({ data: SKILLS, meta: { total: SKILLS.length } });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("SkillsListPage (R483)", () => {
  it("cards render difficulty chip class, tags, and detail links", async () => {
    route();
    render(<SkillsListPage />, { wrapper: wrapper() });
    await screen.findByText("Prompting");
    expect(screen.getByText("beginner").className).toContain("bg-green-100");
    expect(screen.getByText("expert").className).toContain("bg-red-100");
    expect(screen.getByText("ai")).toBeTruthy();
    expect(screen.getByText("Prompting").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/skills/s-1",
    );
  });

  it("search + difficulty + cohort filters combine into one querystring", async () => {
    const calls: string[] = [];
    route(calls, [{ id: "c-1", name: "Fall" }]);
    render(<SkillsListPage />, { wrapper: wrapper() });
    await screen.findByText("Prompting");
    fireEvent.change(screen.getByPlaceholderText("Search skills..."), {
      target: { value: "comp" },
    });
    const selects = screen.getAllByRole("combobox");
    fireEvent.change(selects[0] as HTMLElement, { target: { value: "expert" } });
    fireEvent.change(selects[1] as HTMLElement, { target: { value: "c-1" } });
    await waitFor(() =>
      expect(
        calls.some((c) => c === "/orgs/o-1/skills?q=comp&difficulty=expert&cohort_id=c-1"),
      ).toBe(true),
    );
    // no-filter baseline has NO stray "?"
    expect(calls.some((c) => c === "/orgs/o-1/skills")).toBe(true);
  });

  it("cohort select hidden without cohorts; empty + error states", async () => {
    route();
    const first = render(<SkillsListPage />, { wrapper: wrapper() });
    await first.findByText("Prompting");
    expect(screen.getAllByRole("combobox").length).toBe(1); // difficulty only
    first.unmount();

    vi.clearAllMocks();
    api.mockImplementation(((rawPath: unknown) => {
      if (String(rawPath).includes("my-cohorts")) return Promise.resolve({ data: [] });
      return Promise.resolve({ data: [], meta: { total: 0 } });
    }) as typeof apiWithAuth);
    const second = render(<SkillsListPage />, { wrapper: wrapper() });
    expect(await second.findByText("No skills found.")).toBeTruthy();
    second.unmount();

    vi.clearAllMocks();
    api.mockRejectedValue(new Error("down"));
    render(<SkillsListPage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toContain("Failed to load skills"));
  });
});
