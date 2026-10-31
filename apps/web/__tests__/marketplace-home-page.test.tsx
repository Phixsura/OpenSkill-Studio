import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceHomePage } from "@/components/marketplace-home-page";

describe("MarketplaceHomePage", () => {
  it("renders home", () => {
    const { container } = render(
      <MarketplaceHomePage heroTitle="OpenSkill Marketplace" heroSubtitle="500 apps"
        heroCta="Explore" appsDisplay="500" devsDisplay="200"
        onSearch={vi.fn()} onCategory={vi.fn()}
        featured={[{ name: "Slack Bot", icon: "💬", rating: 4.8, category: "comm" }]}
        categories={[{ id: "tools", label: "Tools", icon: "🛠️", count: 120 }]}
        trending={[]} newApps={[]} />
    );
    expect(container.textContent).toContain("OpenSkill Marketplace");
    expect(container.textContent).toContain("500 apps");
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("Tools");
    expect(container.textContent).toContain("200 developers");
  });
});
