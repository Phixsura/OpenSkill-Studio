import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useParams: () => ({ appId: "app-123" }),
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
}));

vi.mock("@/lib/api", () => ({
  apiWithAuth: { get: vi.fn().mockResolvedValue({ data: { data: {
    id: "app-123", name: "Test App", slug: "test-app", status: "published",
    category: "connector", description: "A test app", visibility: "public",
  } } }) },
}));

import DeveloperAppDetailPage from "@/app/(dashboard)/dashboard/developer/apps/[appId]/page";

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("DeveloperAppDetailPage", () => {
  it("renders without crashing", () => {
    const { container } = render(<DeveloperAppDetailPage />, { wrapper: makeWrapper() });
    expect(container).toBeTruthy();
  });

  it("has structure", () => {
    const { container } = render(<DeveloperAppDetailPage />, { wrapper: makeWrapper() });
    expect(container.querySelectorAll("div").length).toBeGreaterThan(0);
  });
});
