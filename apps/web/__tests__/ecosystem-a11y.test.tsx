import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
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
import ChangesPage from "@/app/(dashboard)/dashboard/ecosystem/changes/page";
import ComparePage from "@/app/(dashboard)/dashboard/ecosystem/compare/page";
import PricingPage from "@/app/(dashboard)/dashboard/ecosystem/pricing/page";
import SecurityPage from "@/app/(dashboard)/dashboard/ecosystem/security/page";
import SourcesPage from "@/app/(dashboard)/dashboard/ecosystem/sources/page";
import WatchlistsPage from "@/app/(dashboard)/dashboard/ecosystem/watchlists/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const PAGES: [string, () => ReactNode][] = [
  ["sources", () => <SourcesPage />],
  ["catalog", () => <CatalogPage />],
  ["changes", () => <ChangesPage />],
  ["pricing", () => <PricingPage />],
  ["benchmarks", () => <BenchmarksPage />],
  ["compare", () => <ComparePage />],
  ["security", () => <SecurityPage />],
  ["watchlists", () => <WatchlistsPage />],
];

beforeEach(() => {
  vi.clearAllMocks();
  api.mockResolvedValue({ data: [], meta: { total: 0 } });
});

describe("Ecosystem a11y smoke (every control has an accessible name)", () => {
  for (const [name, factory] of PAGES) {
    it(`${name}: selects labeled, buttons named, inputs named`, async () => {
      const { container, unmount } = render(<>{factory()}</>, { wrapper: wrapper() });
      // Let initial queries settle
      await new Promise((r) => setTimeout(r, 0));
      for (const el of Array.from(container.querySelectorAll("select"))) {
        expect(el.getAttribute("aria-label"), `unlabeled <select> on ${name}`).toBeTruthy();
      }
      for (const el of Array.from(container.querySelectorAll("button"))) {
        const accessible =
          (el.textContent ?? "").trim().length > 0 || el.getAttribute("aria-label");
        expect(accessible, `nameless <button> on ${name}`).toBeTruthy();
      }
      for (const el of Array.from(container.querySelectorAll("input"))) {
        const accessible =
          el.getAttribute("aria-label") ||
          el.getAttribute("placeholder") ||
          el.closest("label") !== null;
        expect(accessible, `nameless <input> on ${name}`).toBeTruthy();
      }
      unmount();
    });
  }
});
