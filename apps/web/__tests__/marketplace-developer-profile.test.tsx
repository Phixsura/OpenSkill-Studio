import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useParams: () => ({ slug: "test-dev" }),
}));

import DeveloperProfilePage from "@/app/(public)/marketplace/developers/[slug]/page";

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("DeveloperProfilePage", () => {
  it("renders without crashing", () => {
    const { container } = render(<DeveloperProfilePage />, { wrapper: makeWrapper() });
    expect(container).toBeTruthy();
  });

  it("has structure", () => {
    const { container } = render(<DeveloperProfilePage />, { wrapper: makeWrapper() });
    expect(container.querySelectorAll("div").length).toBeGreaterThan(0);
  });
});
