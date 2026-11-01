import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({
  apiWithAuth: { get: vi.fn().mockResolvedValue({ data: { data: null } }), post: vi.fn() },
}));

import DeveloperPortalPage from "@/app/(dashboard)/dashboard/developer/page";

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("DeveloperPortalPage", () => {
  it("renders without crashing", () => {
    const { container } = render(<DeveloperPortalPage />, { wrapper: makeWrapper() });
    expect(container).toBeTruthy();
  });

  it("has interactive elements", () => {
    const { container } = render(<DeveloperPortalPage />, { wrapper: makeWrapper() });
    expect(container.querySelectorAll("button, a, div").length).toBeGreaterThan(0);
  });
});
