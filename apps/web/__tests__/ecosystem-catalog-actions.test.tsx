import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
let searchParams = new URLSearchParams();
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/ecosystem/catalog",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useSearchParams: () => searchParams,
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import CatalogPage from "@/app/(dashboard)/dashboard/ecosystem/catalog/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const ENTITY = "E".repeat(26);

beforeEach(() => {
  vi.clearAllMocks();
  searchParams = new URLSearchParams();
  api.mockImplementation((path: string, init?: RequestInit) => {
    if (/\/ecosystem\/catalog\/\w+\?limit/.test(path) && !init)
      return Promise.resolve({
        data: [
          {
            id: ENTITY,
            canonical_name: "Verified Gen",
            lifecycle_status: "verified",
            sunset_at: null,
            aliases: [],
          },
        ],
        meta: { total: 1 },
      });
    if (path.includes("/score-history")) return Promise.resolve({ data: { points: [] } });
    if (path.includes("/scorecard")) return Promise.resolve({ data: { score: 1, checks: [] } });
    if (path.includes("/pricing/history"))
      return Promise.resolve({ data: { series: {}, trends: {} } });
    return Promise.resolve({ data: [] });
  });
});

describe("Catalog actions wiring (ADR-016 §12 UI)", () => {
  it("quick Watch POSTs kind+id and flips to Watching", async () => {
    render(<CatalogPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText(/Watch$/));
    await new Promise((r) => setTimeout(r, 0));
    const call = api.mock.calls.find(
      (c) =>
        c[0] === "/ecosystem/watchlists/quick-watch" && (c[1] as RequestInit)?.method === "POST",
    );
    expect(call).toBeDefined();
    const body = JSON.parse((call![1] as RequestInit).body as string);
    expect(body.target_kind).toBe("model");
    expect(body.target_id).toBe(ENTITY);
    expect(await screen.findByText(/Watching/)).toBeDefined();
  });

  it("lifecycle move POSTs to_status; deprecation carries a reason", async () => {
    render(<CatalogPage />, { wrapper: wrapper() });
    const select = await screen.findByLabelText("Lifecycle transition");
    fireEvent.change(select, { target: { value: "deprecated" } });
    await new Promise((r) => setTimeout(r, 0));
    const call = api.mock.calls.find(
      (c) =>
        typeof c[0] === "string" &&
        (c[0] as string).endsWith(`/${ENTITY}/lifecycle`) &&
        (c[1] as RequestInit)?.method === "POST",
    );
    expect(call).toBeDefined();
    const body = JSON.parse((call![1] as RequestInit).body as string);
    expect(body.to_status).toBe("deprecated");
    expect(body.reason).toBe("manual_decision");
  });

  it("merge button stays disabled until a full 26-char survivor id is typed", async () => {
    render(<CatalogPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Inspect"));
    const input = await screen.findByPlaceholderText(/merge into entity id/);
    const button = screen.getByText("Merge duplicate → survivor") as HTMLButtonElement;
    fireEvent.change(input, { target: { value: "TOOSHORT" } });
    expect(button.disabled).toBe(true);
    fireEvent.change(input, { target: { value: "S".repeat(26) } });
    expect(button.disabled).toBe(false);
    fireEvent.click(button);
    await new Promise((r) => setTimeout(r, 0));
    expect(
      api.mock.calls.some(
        (c) =>
          typeof c[0] === "string" &&
          (c[0] as string).endsWith(`/${ENTITY}/merge-into/${"S".repeat(26)}`) &&
          (c[1] as RequestInit)?.method === "POST",
      ),
    ).toBe(true);
  });

  it("Inspect panel offers a per-entity Atom subscribe link", async () => {
    render(<CatalogPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Inspect"));
    const link = (await screen.findByText(/subscribe \(.atom\)/)) as HTMLAnchorElement;
    expect(link.getAttribute("href")).toBe(
      `/api/v1/ecosystem/export/changes.atom?entity_id=${ENTITY}`,
    );
    const changesLink = (await screen.findByText(/view changes/)) as HTMLAnchorElement;
    expect(changesLink.closest("a")!.getAttribute("href")).toBe(
      `/dashboard/ecosystem/changes?entity=${ENTITY}`,
    );
  });

  it("deep link to an entity beyond the loaded pages fetches it directly", async () => {
    const HIDDEN = "H".repeat(26);
    searchParams = new URLSearchParams({ kind: "models", entity: HIDDEN });
    api.mockImplementation((path: string, init?: RequestInit) => {
      if (/\/ecosystem\/catalog\/\w+\?limit/.test(path) && !init)
        return Promise.resolve({
          data: [
            {
              id: ENTITY,
              canonical_name: "Verified Gen",
              lifecycle_status: "verified",
              sunset_at: null,
              aliases: [],
            },
          ],
          meta: { total: 500 },
        });
      if (path === `/ecosystem/catalog/models/${HIDDEN}`)
        return Promise.resolve({
          data: {
            id: HIDDEN,
            canonical_name: "Hidden Deep Entity",
            lifecycle_status: "verified",
            sunset_at: null,
            aliases: [],
          },
        });
      if (path.includes("/score-history")) return Promise.resolve({ data: { points: [] } });
      if (path.includes("/scorecard")) return Promise.resolve({ data: { score: 1, checks: [] } });
      if (path.includes("/pricing/history"))
        return Promise.resolve({ data: { series: {}, trends: {} } });
      return Promise.resolve({ data: [] });
    });
    render(<CatalogPage />, { wrapper: wrapper() });
    // the Inspect panel opens for the fetched entity, not silently dropped
    expect(await screen.findByText(/Source conflicts for Hidden Deep Entity/)).toBeDefined();
  });

  it("Inspect panel closes via the close button", async () => {
    render(<CatalogPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Inspect"));
    await screen.findByText(/Source conflicts for/);
    fireEvent.click(screen.getByLabelText("Close inspect panel"));
    expect(screen.queryByText(/Source conflicts for/)).toBeNull();
  });

  it("Load more appends the next offset page", async () => {
    api.mockImplementation((path: string, init?: RequestInit) => {
      if (/\/ecosystem\/catalog\/\w+\?limit=100&offset=0/.test(path) && !init)
        return Promise.resolve({
          data: [
            {
              id: ENTITY,
              canonical_name: "Page One Gen",
              lifecycle_status: "verified",
              sunset_at: null,
              aliases: [],
            },
          ],
          meta: { total: 2 },
        });
      if (/offset=1/.test(path) && !init)
        return Promise.resolve({
          data: [
            {
              id: "F".repeat(26),
              canonical_name: "Page Two Gen",
              lifecycle_status: "verified",
              sunset_at: null,
              aliases: [],
            },
          ],
          meta: { total: 2 },
        });
      return Promise.resolve({ data: [] });
    });
    render(<CatalogPage />, { wrapper: wrapper() });
    await screen.findByText("Page One Gen");
    fireEvent.click(screen.getByText("Load more"));
    await screen.findByText("Page Two Gen");
    // first page stays appended
    expect(screen.getByText("Page One Gen")).toBeDefined();
  });

  it("Inspect shows the availability status badge from probe history", async () => {
    api.mockImplementation((path: string, init?: RequestInit) => {
      if (/\/ecosystem\/catalog\/\w+\?limit/.test(path) && !init)
        return Promise.resolve({
          data: [
            {
              id: ENTITY,
              canonical_name: "Verified Gen",
              lifecycle_status: "verified",
              sunset_at: null,
              aliases: [],
            },
          ],
          meta: { total: 1 },
        });
      if (path.includes("/availability/uptime"))
        return Promise.resolve({
          data: {
            current_status: "degraded",
            uptime_pct: 97.1,
            daily: [
              { date: "2026-09-24", worst_status: "operational" },
              { date: "2026-09-25", worst_status: "unreachable" },
            ],
          },
        });
      if (path.includes("/score-history")) return Promise.resolve({ data: { points: [] } });
      if (path.includes("/scorecard")) return Promise.resolve({ data: { score: 1, checks: [] } });
      if (path.includes("/pricing/history"))
        return Promise.resolve({ data: { series: {}, trends: {} } });
      return Promise.resolve({ data: [] });
    });
    render(<CatalogPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Inspect"));
    expect(await screen.findByText("degraded")).toBeDefined();
    // daily strip renders with per-day tooltips
    expect(await screen.findByText(/97.1% uptime/)).toBeDefined();
    expect(screen.getByTitle("2026-09-25: unreachable")).toBeDefined();
  });

  it("Inspect shows curated facts as pills", async () => {
    api.mockImplementation((path: string, init?: RequestInit) => {
      if (/\/ecosystem\/catalog\/\w+\?limit/.test(path) && !init)
        return Promise.resolve({
          data: [
            {
              id: ENTITY,
              canonical_name: "Verified Gen",
              lifecycle_status: "verified",
              sunset_at: null,
              aliases: [],
              metadata: { curated: { license: { value: "MIT", decided_at: "2026-09-25" } } },
            },
          ],
          meta: { total: 1 },
        });
      if (path.includes("/availability/uptime"))
        return Promise.resolve({
          data: { current_status: "operational", uptime_pct: 99, daily: [] },
        });
      if (path.includes("/score-history")) return Promise.resolve({ data: { points: [] } });
      if (path.includes("/scorecard")) return Promise.resolve({ data: { score: 1, checks: [] } });
      if (path.includes("/pricing/history"))
        return Promise.resolve({ data: { series: {}, trends: {} } });
      return Promise.resolve({ data: [] });
    });
    render(<CatalogPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Inspect"));
    expect(await screen.findByText(/license: MIT/)).toBeDefined();
  });

  it("adopting a conflict value POSTs resolve-conflict with field + value", async () => {
    api.mockImplementation((path: string, init?: RequestInit) => {
      if (/\/ecosystem\/catalog\/\w+\?limit/.test(path) && !init)
        return Promise.resolve({
          data: [
            {
              id: ENTITY,
              canonical_name: "Verified Gen",
              lifecycle_status: "verified",
              sunset_at: null,
              aliases: [],
            },
          ],
          meta: { total: 1 },
        });
      if (path.includes("/conflicts"))
        return Promise.resolve({
          data: [{ field: "license", values: { MIT: ["s1"], GPL: ["s2"] }, curated: null }],
        });
      if (path.includes("/availability/uptime"))
        return Promise.resolve({
          data: { current_status: "operational", uptime_pct: null, daily: [] },
        });
      if (path.includes("/score-history")) return Promise.resolve({ data: { points: [] } });
      if (path.includes("/scorecard")) return Promise.resolve({ data: { score: 1, checks: [] } });
      if (path.includes("/pricing/history"))
        return Promise.resolve({ data: { series: {}, trends: {} } });
      return Promise.resolve({ data: [] });
    });
    render(<CatalogPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Inspect"));
    fireEvent.click(await screen.findByText(/MIT/));
    await new Promise((r) => setTimeout(r, 0));
    const call = api.mock.calls.find(
      (c) =>
        typeof c[0] === "string" &&
        (c[0] as string).endsWith(`/${ENTITY}/resolve-conflict`) &&
        (c[1] as RequestInit)?.method === "POST",
    );
    expect(call).toBeDefined();
    const body = JSON.parse((call![1] as RequestInit).body as string);
    expect(body.field).toBe("license");
    expect(body.chosen_value).toBe("MIT");
  });
});
