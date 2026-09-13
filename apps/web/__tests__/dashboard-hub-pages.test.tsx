import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import ProjectsHub from "@/app/(dashboard)/dashboard/projects/page";
import SkillsHub from "@/app/(dashboard)/dashboard/skills/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const ORGS = [
  { id: "o-1", name: "Acme" },
  { id: "o-2", name: "Beta Lab" },
];

beforeEach(() => vi.clearAllMocks());

describe("Dashboard hub pages (R484)", () => {
  it("projects hub links each org to its org-scoped projects list", async () => {
    api.mockResolvedValue({ data: ORGS });
    render(<ProjectsHub />, { wrapper: wrapper() });
    await screen.findByText("Acme");
    expect(screen.getByText("Acme").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/projects",
    );
    expect(screen.getByText("Beta Lab").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-2/projects",
    );
  });

  it("skills hub links each org to its org-scoped skills list", async () => {
    api.mockResolvedValue({ data: ORGS });
    render(<SkillsHub />, { wrapper: wrapper() });
    await screen.findByText("Acme");
    expect(screen.getByText("Acme").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/skills",
    );
  });

  it("no orgs -> join prompt on both hubs", async () => {
    api.mockResolvedValue({ data: [] });
    const first = render(<ProjectsHub />, { wrapper: wrapper() });
    expect(await first.findByText(/Join an organization to see project/)).toBeTruthy();
    first.unmount();
    render(<SkillsHub />, { wrapper: wrapper() });
    expect(await screen.findByText(/Join an organization/)).toBeTruthy();
  });
});
