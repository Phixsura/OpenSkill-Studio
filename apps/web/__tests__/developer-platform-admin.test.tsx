import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({
  apiWithAuth: { get: vi.fn().mockResolvedValue({ data: { data: {
    developer_accounts: 5,
    total_apps: 12,
    apps_by_status: { published: 8, draft: 4 },
    active_installations: 20,
    executions_24h: { total: 100, failed: 2, error_rate_pct: 2.0 },
  } } }) },
}));

import DeveloperPlatformPage from "@/app/(dashboard)/platform/developer-platform/page";

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("DeveloperPlatformPage", () => {
  it("renders without crashing", () => {
    const { container } = render(<DeveloperPlatformPage />, { wrapper: makeWrapper() });
    expect(container).toBeTruthy();
  });

  it("has dashboard structure", () => {
    const { container } = render(<DeveloperPlatformPage />, { wrapper: makeWrapper() });
    const elements = container.querySelectorAll("h1, h2, h3, div, section");
    expect(elements.length).toBeGreaterThan(0);
  });
});
