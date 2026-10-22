import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn(), prefetch: vi.fn() }),
  usePathname: () => "/dashboard/developer/apps",
  useSearchParams: () => new URLSearchParams(),
}));

vi.mock("@/lib/api", () => ({
  apiWithAuth: { get: vi.fn().mockResolvedValue({ data: { data: [] } }) },
}));

import DeveloperAppsPage from "@/app/(dashboard)/dashboard/developer/apps/page";

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("DeveloperAppsPage", () => {
  it("renders without crashing", () => {
    const { container } = render(<DeveloperAppsPage />, { wrapper: makeWrapper() });
    expect(container).toBeTruthy();
  });

  it("shows create button or link", () => {
    const { container } = render(<DeveloperAppsPage />, { wrapper: makeWrapper() });
    const buttons = container.querySelectorAll("button, a");
    expect(buttons.length).toBeGreaterThan(0);
  });
});
