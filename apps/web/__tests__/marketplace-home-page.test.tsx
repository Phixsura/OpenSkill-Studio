import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceHomePage } from "@/components/marketplace-home-page";

describe("MarketplaceHomePage", () => {
  it("renders marketplace home", () => {
    const { container } = render(
      <MarketplaceHomePage heroTitle="OpenSkill Marketplace" heroSubtitle="Discover apps"
        appsDisplay="5,200" devsDisplay="1,800"
        featured={[{ id: "a1", name: "SuperApp", icon: "🚀", tagline: "Do more", rating: 4.8 }]}
        trending={[{ id: "a2", name: "HotApp", icon: "🔥", growthPct: 250 }]}
        categories={[{ id: "tools", name: "Tools", icon: "🔧", count: 150 }]}
        newApps={[{ id: "a3", name: "FreshApp", icon: "🆕" }]}
        onSelectApp={vi.fn()} onSelectCategory={vi.fn()} />
    );
    expect(container.textContent).toContain("OpenSkill Marketplace");
    expect(container.textContent).toContain("5,200");
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("HotApp");
    expect(container.textContent).toContain("250%");
    expect(container.textContent).toContain("Tools");
    expect(container.textContent).toContain("FreshApp");
  });
});
