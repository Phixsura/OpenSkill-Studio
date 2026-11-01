import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppDetailPageLayout } from "@/components/app-detail-page-layout";

describe("AppDetailPageLayout", () => {
  const props = {
    header: { name: "Auth SDK", developer: "Alice", tagline: "Easy auth",
      rating: 4.7, install_count: 8500, price: 0, version: "2.1" },
    description: "Authentication made easy for every project.",
    reviews: { total: 120, avg_rating: 4.5, recent: [] },
    relatedApps: [{ id: "a2", name: "OAuth Kit" }],
    permissions: ["read:profile"],
    tabs: ["Overview", "Reviews", "Changelog"],
  };
  it("renders complete page", () => {
    const { container } = render(
      <AppDetailPageLayout {...props} onInstall={vi.fn()} onTabChange={vi.fn()} onRelatedClick={vi.fn()} />
    );
    expect(container.textContent).toContain("Auth SDK");
    expect(container.textContent).toContain("by Alice");
    expect(container.textContent).toContain("Install Free");
    expect(container.textContent).toContain("Overview");
    expect(container.textContent).toContain("Reviews (120)");
    expect(container.textContent).toContain("⭐ 4.5");
    expect(container.textContent).toContain("OAuth Kit");
    expect(container.textContent).toContain("Authentication made easy");
  });
});
