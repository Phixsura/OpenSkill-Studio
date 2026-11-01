import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({
  apiWithAuth: {
    get: vi.fn().mockResolvedValue({ data: { data: null } }),
    post: vi.fn().mockResolvedValue({ data: { data: {} } }),
  },
}));

import {
  useDeveloperAccount,
  useDeveloperApps,
  useMarketplaceApps,
  useFeaturedApps,
} from "@/lib/developer-api-hooks";

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("Developer API Hooks", () => {
  it("useDeveloperAccount returns query", () => {
    const { result } = renderHook(() => useDeveloperAccount(), { wrapper: makeWrapper() });
    expect(result.current).toHaveProperty("isLoading");
    expect(result.current).toHaveProperty("data");
  });

  it("useDeveloperApps returns query", () => {
    const { result } = renderHook(() => useDeveloperApps(), { wrapper: makeWrapper() });
    expect(result.current).toHaveProperty("isLoading");
  });

  it("useMarketplaceApps returns query", () => {
    const { result } = renderHook(() => useMarketplaceApps(), { wrapper: makeWrapper() });
    expect(result.current).toHaveProperty("isLoading");
  });

  it("useFeaturedApps returns query", () => {
    const { result } = renderHook(() => useFeaturedApps(), { wrapper: makeWrapper() });
    expect(result.current).toHaveProperty("isLoading");
  });

  it("useMarketplaceApps with params", () => {
    const { result } = renderHook(
      () => useMarketplaceApps({ query: "test", category: "connector", page: 1 }),
      { wrapper: makeWrapper() }
    );
    expect(result.current).toHaveProperty("isLoading");
  });
});
