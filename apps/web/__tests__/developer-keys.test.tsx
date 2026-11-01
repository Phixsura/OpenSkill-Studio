import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({
  apiWithAuth: { get: vi.fn().mockResolvedValue({ data: { data: [] } }) },
}));

import DeveloperKeysPage from "@/app/(dashboard)/dashboard/developer/keys/page";

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("DeveloperKeysPage", () => {
  it("renders", () => {
    const { container } = render(<DeveloperKeysPage />, { wrapper: makeWrapper() });
    expect(container).toBeTruthy();
  });

  it("has structure", () => {
    const { container } = render(<DeveloperKeysPage />, { wrapper: makeWrapper() });
    expect(container.querySelectorAll("div").length).toBeGreaterThan(0);
  });
});
