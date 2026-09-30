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
  usePathname: () => "/dashboard/ecosystem",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import BenchmarksPage from "@/app/(dashboard)/dashboard/ecosystem/benchmarks/page";
import CatalogPage from "@/app/(dashboard)/dashboard/ecosystem/catalog/page";
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

beforeEach(() => {
  vi.clearAllMocks();
  api.mockResolvedValue({ data: [], meta: { total: 0 } });
});

describe("Admin action wiring (ADR-016 §69)", () => {
  it("advisory registration POSTs the full structured payload", async () => {
    render(<SecurityPage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByPlaceholderText(/CVE-2026/), {
      target: { value: "CVE-2026-9999" },
    });
    fireEvent.change(screen.getByPlaceholderText("title"), {
      target: { value: "RCE in nodes" },
    });
    fireEvent.change(screen.getByPlaceholderText(/affected name/), {
      target: { value: "acme-nodes" },
    });
    fireEvent.change(screen.getByPlaceholderText(/range e.g./), {
      target: { value: ">=1.0 <2.0" },
    });
    fireEvent.click(screen.getByText("Register advisory"));
    await new Promise((r) => setTimeout(r, 0));
    const call = api.mock.calls.find(
      (c) => c[0] === "/ecosystem/security/advisories" && (c[1] as RequestInit)?.method === "POST",
    );
    expect(call).toBeDefined();
    const body = JSON.parse((call![1] as RequestInit).body as string);
    expect(body.advisory_ref).toBe("CVE-2026-9999");
    expect(body.affected_range).toBe(">=1.0 <2.0");
  });

  it("suite import surfaces API rejection", async () => {
    const { ApiError } = await import("@/lib/api");
    const ApiErrorCtor = ApiError as unknown as new (message: string) => Error;
    api.mockImplementation((path: string, init?: RequestInit) => {
      if (path === "/ecosystem/benchmark/suites/import" && init?.method === "POST")
        return Promise.reject(new ApiErrorCtor("Suite key already exists"));
      return Promise.resolve({ data: [] });
    });
    render(<BenchmarksPage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByPlaceholderText(/Paste an exported suite JSON/), {
      target: { value: '{"format":"openskill.benchmark-suite"}' },
    });
    fireEvent.click(screen.getByText("Import suite"));
    expect(await screen.findByText(/Suite key already exists/)).toBeDefined();
  });

  it("duplicates scan renders suspected pairs", async () => {
    api.mockImplementation((path: string) => {
      if (path.includes("/duplicates"))
        return Promise.resolve({
          data: [
            {
              a: { id: "A".repeat(26), canonical_name: "Flux Image", lifecycle_status: "verified" },
              b: { id: "B".repeat(26), canonical_name: "FluxImage", lifecycle_status: "verified" },
              similarity: 0.91,
            },
          ],
        });
      return Promise.resolve({ data: [], meta: { total: 0 } });
    });
    render(<CatalogPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Scan for duplicates"));
    expect(await screen.findByText("Flux Image")).toBeDefined();
    expect(screen.getByText("FluxImage")).toBeDefined();
    expect(screen.getByText(/similarity 0.91/)).toBeDefined();
  });
});
