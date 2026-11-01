import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceHomepage } from "@/components/marketplace-homepage";

describe("MarketplaceHomepage", () => {
  const props = {
    hero: { title: "OpenSkill Marketplace", subtitle: "Discover apps", cta: "Explore", app_count: 500, developer_count: 200 },
    featuredApps: [{ id: "a1", name: "Auth SDK" }],
    trendingApps: [{ id: "t1", name: "Charts Pro" }],
    categories: [{ id: "tools", name: "Tools", count: 50 }],
    stats: { total_apps: 500, total_developers: 200, total_installs: 100000, avg_rating: 4.5 },
    announcements: [{ title: "New feature!", body: "Dark mode is here" }],
  };
  it("renders complete homepage", () => {
    const { container } = render(
      <MarketplaceHomepage {...props} onSearch={vi.fn()} onAppClick={vi.fn()} />
    );
    expect(container.textContent).toContain("OpenSkill Marketplace");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("⭐ Featured Apps");
    expect(container.textContent).toContain("Auth SDK");
    expect(container.textContent).toContain("🔥 Trending Now");
    expect(container.textContent).toContain("Charts Pro");
    expect(container.textContent).toContain("📂 Categories");
    expect(container.textContent).toContain("Tools");
    expect(container.textContent).toContain("📢 Announcements");
    expect(container.textContent).toContain("Dark mode is here");
  });
});
