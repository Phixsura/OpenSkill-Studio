import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/ecosystem/security",
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import SecurityPage from "@/app/(dashboard)/dashboard/ecosystem/security/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

beforeEach(() => vi.clearAllMocks());

describe("Ecosystem security advisories page (ADR-016 §38)", () => {
  it("lists advisories and resolves affected entities with fail-open label", async () => {
    api.mockImplementation((path: string) => {
      if (path.startsWith("/ecosystem/security/advisories?"))
        return Promise.resolve({
          data: [
            {
              id: "adv1",
              advisory_ref: "CVE-2026-0001",
              title: "RCE in acme-nodes",
              severity: "critical",
              affected_kind: "node_package",
              affected_ref: "acme-nodes",
              affected_range: ">=1.0 <2.4",
              fixed_in: "2.4.0",
              status: "open",
              created_at: "2026-09-20T00:00:00Z",
            },
          ],
        });
      if (path.includes("/affected"))
        return Promise.resolve({
          data: [
            {
              entity_kind: "node_package",
              entity_id: "N".repeat(26),
              canonical_name: "acme-nodes",
              version: "nightly",
              range_match: "unknown_fail_open",
              lifecycle_status: "verified",
            },
          ],
        });
      return Promise.resolve({ data: [] });
    });
    render(<SecurityPage />, { wrapper: wrapper() });
    expect(await screen.findByText("CVE-2026-0001")).toBeDefined();
    expect(screen.getByText("RCE in acme-nodes")).toBeDefined();
    fireEvent.click(screen.getByText("Affected entities"));
    expect(await screen.findByText("acme-nodes")).toBeDefined();
    expect(screen.getByText(/unknown \(fail-open\)/)).toBeDefined();
  });

  it("Mark mitigated / Dismiss POST the status transition; closed advisories offer neither", async () => {
    const adv = (id: string, status: string) => ({
      id,
      advisory_ref: `CVE-2026-000${id}`,
      title: "RCE",
      severity: "high",
      affected_kind: "node_package",
      affected_ref: "acme-nodes",
      affected_range: null,
      fixed_in: null,
      status,
      created_at: "2026-09-20T00:00:00Z",
    });
    api.mockImplementation((path: string) => {
      if (path.startsWith("/ecosystem/security/advisories?"))
        return Promise.resolve({ data: [adv("a1", "open"), adv("a2", "mitigated")] });
      return Promise.resolve({ data: [] });
    });
    render(<SecurityPage />, { wrapper: wrapper() });
    // Only the open advisory offers transitions
    expect(await screen.findAllByText("Mark mitigated")).toHaveLength(1);
    fireEvent.click(screen.getByText("Mark mitigated"));
    await new Promise((r) => setTimeout(r, 0));
    expect(
      api.mock.calls.some(
        (c) =>
          c[0] === "/ecosystem/security/advisories/a1/status?to_status=mitigated" &&
          (c[1] as RequestInit)?.method === "POST",
      ),
    ).toBe(true);
    fireEvent.click(screen.getByText("Dismiss"));
    await new Promise((r) => setTimeout(r, 0));
    expect(
      api.mock.calls.some(
        (c) =>
          c[0] === "/ecosystem/security/advisories/a1/status?to_status=dismissed" &&
          (c[1] as RequestInit)?.method === "POST",
      ),
    ).toBe(true);
  });

  it("affected entities deep-link to their change feed", async () => {
    api.mockImplementation((path: string) => {
      if (path.startsWith("/ecosystem/security/advisories?"))
        return Promise.resolve({
          data: [
            {
              id: "advL",
              advisory_ref: "CVE-2026-0002",
              title: "x",
              severity: "high",
              affected_kind: "model",
              affected_ref: "gen",
              affected_range: null,
              fixed_in: null,
              status: "open",
              created_at: "2026-09-20T00:00:00Z",
            },
          ],
        });
      if (path.includes("/affected"))
        return Promise.resolve({
          data: [
            {
              entity_kind: "model",
              entity_id: "A".repeat(26),
              canonical_name: "gen",
              version: null,
              range_match: "name_only",
              lifecycle_status: "verified",
            },
          ],
        });
      return Promise.resolve({ data: [] });
    });
    render(<SecurityPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Affected entities"));
    const link = await screen.findByText("changes");
    expect(link.closest("a")!.getAttribute("href")).toBe(
      `/dashboard/ecosystem/changes?entity=${"A".repeat(26)}`,
    );
  });
});
