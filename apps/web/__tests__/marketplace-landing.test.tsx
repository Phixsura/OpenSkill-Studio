import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceLanding } from "@/components/marketplace-landing";

describe("MarketplaceLanding", () => {
  const featured = [{ id: "a1", name: "SuperApp", icon: "🚀", tagline: "Do more" }];
  const categories = [{ id: "tools", name: "Tools", icon: "🔧", appCount: 150 }];
  const stats = { totalApps: 500, totalDevelopers: 200, totalDownloads: 1000000 };
  it("renders landing page", () => {
    const { container } = render(
      <MarketplaceLanding featured={featured} categories={categories} stats={stats}
        onSelectApp={vi.fn()} onSelectCategory={vi.fn()} />
    );
    expect(container.textContent).toContain("Discover apps");
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("Tools");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("1,000,000");
  });
});
