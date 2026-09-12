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
vi.mock("@/lib/api", () => ({
  api: vi.fn(),
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import WorkflowInstallationsPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/workflow-installations/page";
import { api, apiWithAuth } from "@/lib/api";

const authApi = vi.mocked(apiWithAuth);
const pubApi = vi.mocked(api);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const INSTALLS = [
  {
    id: "i-1",
    pack_id: "pk-pub",
    installed_version: "1.2.0",
    status: "active",
    locally_modified: true,
    installed_at: "2026-09-01T00:00:00Z",
  },
  {
    id: "i-2",
    pack_id: "pk-priv",
    installed_version: "0.9.0",
    status: "forked",
    locally_modified: false,
    installed_at: "2026-09-02T00:00:00Z",
  },
  {
    id: "i-3",
    pack_id: null,
    installed_version: "2.0.0",
    status: "removed",
    locally_modified: false,
    installed_at: "2026-09-03T00:00:00Z",
  },
];

function route() {
  authApi.mockImplementation(((rawPath: unknown) => {
    const path = String(rawPath ?? "");
    if (path.includes("workflow-installations"))
      return Promise.resolve({ data: INSTALLS, meta: { total: 3, has_more: false } });
    return Promise.resolve({ data: [] });
  }) as typeof apiWithAuth);
  pubApi.mockImplementation(((rawPath: unknown) => {
    const path = String(rawPath ?? "");
    if (path.includes("/registry/workflow-packs/pk-pub"))
      return Promise.resolve({ data: { id: "pk-pub", name: "Render Farm Pack" } });
    // private pack 404s at the public registry
    return Promise.reject(new Error("404"));
  }) as typeof api);
}

beforeEach(() => vi.clearAllMocks());

describe("WorkflowInstallationsPage (R470)", () => {
  it("pack-name resolution: registry name, ULID fallback on 404, '(pack removed)' for null", async () => {
    route();
    render(<WorkflowInstallationsPage />, { wrapper: wrapper() });
    await screen.findByText("Render Farm Pack"); // resolved via public registry
    const body = document.body.textContent ?? "";
    expect(body).toContain("pk-priv"); // 404 fails silently -> ULID fallback
    expect(body).toContain("(pack removed)"); // null pack_id
    expect(body).toContain("v1.2.0");
    // the modified chip sits ONLY on i-1's row
    const modRow = screen.getByText("Render Farm Pack").closest("a");
    expect(modRow?.textContent).toContain("modified");
    const privRow = screen.getByText("pk-priv").closest("a");
    expect(privRow?.textContent).not.toContain("modified");
    // status chips and detail links
    expect(screen.getByText("forked")).toBeTruthy();
    expect(modRow?.getAttribute("href")).toBe("/dashboard/orgs/o-1/workflow-installations/i-1");
    // no pager at total<=perPage on page 1
    expect(screen.queryByRole("button", { name: "Next" })).toBeNull();
  });

  it("registry lookups are deduped to unique non-null pack ids", async () => {
    route();
    render(<WorkflowInstallationsPage />, { wrapper: wrapper() });
    await screen.findByText("Render Farm Pack");
    const lookups = pubApi.mock.calls.map((c) => String(c[0]));
    expect(lookups.sort()).toEqual([
      "/registry/workflow-packs/pk-priv",
      "/registry/workflow-packs/pk-pub",
    ]); // no null lookup, no duplicates
  });

  it("empty state and error state", async () => {
    authApi.mockResolvedValue({ data: [], meta: { total: 0, has_more: false } });
    const first = render(<WorkflowInstallationsPage />, { wrapper: wrapper() });
    expect(await first.findByText(/No workflow packs installed yet/)).toBeTruthy();
    first.unmount();

    vi.clearAllMocks();
    authApi.mockRejectedValue(new Error("installs down"));
    render(<WorkflowInstallationsPage />, { wrapper: wrapper() });
    await waitFor(() =>
      expect(document.body.textContent).toContain("Failed to load workflow installations"),
    );
  });
});
