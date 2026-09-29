import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
const replaceSpy = vi.fn();
let searchParams = new URLSearchParams();
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/ecosystem/sources",
  useRouter: () => ({ replace: replaceSpy, push: vi.fn() }),
  useSearchParams: () => searchParams,
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import SourcesPage from "@/app/(dashboard)/dashboard/ecosystem/sources/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const SRC = "S".repeat(26);

function source(status: string) {
  return {
    id: SRC,
    name: "HF feed",
    source_type: "registry",
    trust_level: "official",
    base_url: "https://x",
    adapter_key: "huggingface",
    status,
    last_success_at: null,
    consecutive_failures: 0,
    robots_compliant: true,
  };
}

function mockSources(status: string) {
  api.mockImplementation((path: string, init?: RequestInit) => {
    if (path.startsWith("/ecosystem/sources?") && !init)
      return Promise.resolve({ data: [source(status)], meta: { total: 1, limit: 50, offset: 0 } });
    return Promise.resolve({ data: {} });
  });
}

beforeEach(() => vi.clearAllMocks());

describe("Source operator controls (ADR-016 §11 UI)", () => {
  it("Sync now POSTs for an active source and Pause PATCHes status", async () => {
    mockSources("active");
    render(<SourcesPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Sync now"));
    fireEvent.click(screen.getByText("Pause"));
    await new Promise((r) => setTimeout(r, 0));
    expect(
      api.mock.calls.some(
        (c) =>
          c[0] === `/ecosystem/sources/${SRC}/sync` && (c[1] as RequestInit)?.method === "POST",
      ),
    ).toBe(true);
    const patch = api.mock.calls.find(
      (c) => c[0] === `/ecosystem/sources/${SRC}` && (c[1] as RequestInit)?.method === "PATCH",
    );
    expect(patch).toBeDefined();
    expect(JSON.parse((patch![1] as RequestInit).body as string).status).toBe("paused");
  });

  it("Sync now is disabled for a paused source; Resume PATCHes active", async () => {
    mockSources("paused");
    render(<SourcesPage />, { wrapper: wrapper() });
    const sync = (await screen.findByText("Sync now")) as HTMLButtonElement;
    expect(sync.disabled).toBe(true);
    fireEvent.click(screen.getByText("Resume"));
    await new Promise((r) => setTimeout(r, 0));
    const patch = api.mock.calls.find(
      (c) => c[0] === `/ecosystem/sources/${SRC}` && (c[1] as RequestInit)?.method === "PATCH",
    );
    expect(patch).toBeDefined();
    expect(JSON.parse((patch![1] as RequestInit).body as string).status).toBe("active");
  });

  it("Replay POSTs to the replay endpoint (append-only re-parse)", async () => {
    mockSources("active");
    render(<SourcesPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Replay"));
    await new Promise((r) => setTimeout(r, 0));
    expect(
      api.mock.calls.some(
        (c) =>
          c[0] === `/ecosystem/sources/${SRC}/replay` && (c[1] as RequestInit)?.method === "POST",
      ),
    ).toBe(true);
  });

  it("Register source form POSTs the full payload (SSRF-guarded server-side)", async () => {
    mockSources("active");
    render(<SourcesPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Register source"));
    fireEvent.change(screen.getByPlaceholderText("Source name"), {
      target: { value: "HF models feed" },
    });
    fireEvent.change(screen.getByPlaceholderText(/Base URL/), {
      target: { value: "https://huggingface.co/api/models" },
    });
    fireEvent.change(screen.getByLabelText("Source type"), { target: { value: "huggingface" } });
    fireEvent.change(screen.getByLabelText("Trust level"), { target: { value: "community" } });
    fireEvent.change(screen.getByLabelText("Adapter"), { target: { value: "huggingface" } });
    fireEvent.click(screen.getByRole("button", { name: "Create" }));
    await new Promise((r) => setTimeout(r, 0));
    const call = api.mock.calls.find(
      (c) => c[0] === "/ecosystem/sources" && (c[1] as RequestInit)?.method === "POST",
    );
    expect(call).toBeDefined();
    const body = JSON.parse((call![1] as RequestInit).body as string);
    expect(body.name).toBe("HF models feed");
    expect(body.base_url).toBe("https://huggingface.co/api/models");
    expect(body.source_type).toBe("huggingface");
    expect(body.trust_level).toBe("community");
    expect(body.adapter_key).toBe("huggingface");
  });
});

describe("Next-sync visibility (R355)", () => {
  it("overdue active sources show the warning; fresh ones show next-due", async () => {
    const past = new Date(Date.now() - 3 * 60 * 60_000).toISOString();
    const recent = new Date(Date.now() - 5 * 60_000).toISOString();
    api.mockImplementation((path: string) => {
      if (path.startsWith("/ecosystem/sources"))
        return Promise.resolve({
          data: [
            {
              id: "s1",
              name: "Overdue Src",
              source_type: "provider_api",
              trust_level: "official",
              base_url: null,
              adapter_key: "json_catalog",
              status: "active",
              last_success_at: past,
              consecutive_failures: 0,
              robots_compliant: true,
              sync_interval_minutes: 60,
            },
            {
              id: "s2",
              name: "Fresh Src",
              source_type: "provider_api",
              trust_level: "official",
              base_url: null,
              adapter_key: "json_catalog",
              status: "active",
              last_success_at: recent,
              consecutive_failures: 0,
              robots_compliant: true,
              sync_interval_minutes: 1440,
            },
          ],
        });
      return Promise.resolve({ data: [] });
    });
    render(<SourcesPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/sync overdue/)).toBeDefined();
    expect(screen.getByText(/next ≈/)).toBeDefined();
  });
});

describe("Source status filter (R378)", () => {
  it("dropdown sends ?status= to the list endpoint", async () => {
    api.mockImplementation(() => Promise.resolve({ data: [] }));
    render(<SourcesPage />, { wrapper: wrapper() });
    fireEvent.change(await screen.findByLabelText("Filter by source status"), {
      target: { value: "paused" },
    });
    await waitFor(() =>
      expect(
        api.mock.calls.some((c) =>
          String(c[0]).includes("sources?limit=50&offset=0&status=paused"),
        ),
      ).toBe(true),
    );
  });
});

describe("Source list pagination (R387)", () => {
  it("shows count-of-total and Load more fetches the next offset", async () => {
    api.mockImplementation((path: string, init?: RequestInit) => {
      if (String(path).startsWith("/ecosystem/sources?") && !init) {
        const offset = Number(new URLSearchParams(String(path).split("?")[1]).get("offset"));
        return Promise.resolve({
          data: Array.from({ length: 50 }, (_, i) => ({
            ...sourceAt(offset + i),
          })),
          meta: { total: 120, limit: 50, offset },
        });
      }
      return Promise.resolve({ data: [] });
    });
    render(<SourcesPage />, { wrapper: wrapper() });
    expect(await screen.findByText("50 of 120")).toBeTruthy();
    fireEvent.click(screen.getByText("Load more"));
    await waitFor(() =>
      expect(api.mock.calls.some((c) => String(c[0]).includes("limit=50&offset=50"))).toBe(true),
    );
    expect(await screen.findByText("100 of 120")).toBeTruthy();
  });
});

function sourceAt(i: number) {
  return {
    id: `S${String(i).padStart(24, "0")}`,
    name: `Source ${i}`,
    source_type: "github_repo",
    trust_level: "community",
    status: "active",
    last_success_at: null,
    consecutive_failures: 0,
    sync_interval_minutes: 1440,
  };
}

describe("Status filter is shareable URL state (R393)", () => {
  it("?status= in the URL seeds the filter and changing it rewrites the URL", async () => {
    searchParams = new URLSearchParams("status=paused");
    api.mockImplementation(() =>
      Promise.resolve({ data: [], meta: { total: 0, limit: 50, offset: 0 } }),
    );
    render(<SourcesPage />, { wrapper: wrapper() });
    await waitFor(() =>
      expect(api.mock.calls.some((c) => String(c[0]).includes("&status=paused"))).toBe(true),
    );
    fireEvent.change(await screen.findByLabelText("Filter by source status"), {
      target: { value: "error" },
    });
    expect(replaceSpy).toHaveBeenCalledWith("/dashboard/ecosystem/sources?status=error", {
      scroll: false,
    });
    searchParams = new URLSearchParams();
  });
});
