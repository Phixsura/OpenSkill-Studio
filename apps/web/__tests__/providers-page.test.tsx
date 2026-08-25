import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "org-1" }),
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import ProvidersPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/providers/page";
import { apiWithAuth } from "@/lib/api";

const mockApiWithAuth = vi.mocked(apiWithAuth);

function createWrapper() {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("ProvidersPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("shows loading state while queries are pending", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<ProvidersPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Loading...")).toBeDefined();
  });

  it("shows error state when a query fails — not the empty state", async () => {
    mockApiWithAuth.mockRejectedValue(new Error("fail"));
    render(<ProvidersPage />, { wrapper: createWrapper() });
    expect(await screen.findByText(/Failed to load providers/)).toBeDefined();
    expect(screen.queryByText(/No provider connections yet/)).toBeNull();
  });

  it("shows empty state when queries succeed with no connections", async () => {
    mockApiWithAuth.mockResolvedValue({ data: [] });
    render(<ProvidersPage />, { wrapper: createWrapper() });
    expect(await screen.findByText(/No provider connections yet/)).toBeDefined();
    expect(screen.getByText("Providers")).toBeDefined();
  });
});
