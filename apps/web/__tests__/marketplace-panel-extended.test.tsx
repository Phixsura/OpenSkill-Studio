import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/marketplace",
}));

vi.mock("@/lib/api", () => ({
  apiWithAuth: { get: vi.fn().mockResolvedValue({ data: { data: [] } }) },
}));

// Import any marketplace-related component that exists
import { AppCard } from "@/components/app-card";
import { CategoryIcon } from "@/components/category-icon";
import { AppStatusBadge } from "@/components/app-status-badge";

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("Marketplace Components Integration", () => {
  it("AppCard + AppStatusBadge render together", () => {
    const { container } = render(
      <div>
        <AppCard id="1" name="Test" slug="test" description="Desc" category="connector" status="published" />
        <AppStatusBadge status="published" />
      </div>
    );
    expect(container.textContent).toContain("Test");
  });

  it("CategoryIcon renders all types", () => {
    const cats = ["connector", "automation", "analytics"];
    const { container } = render(
      <div>{cats.map(c => <CategoryIcon key={c} category={c} />)}</div>
    );
    expect(container.children[0].childNodes.length).toBe(3);
  });
});
