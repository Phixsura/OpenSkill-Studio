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
  usePathname: () => "/dashboard/ecosystem/sources",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
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
    if (path === "/ecosystem/sources" && !init) return Promise.resolve({ data: [source(status)] });
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
});
