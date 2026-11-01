import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceHome } from "@/components/marketplace-home";

const featured = [
  { id: "f1", name: "Slack Bot Pro", icon: "🤖", tagline: "Ultimate Slack integration" },
];
const sections = [
  { id: "trending", title: "🔥 Trending", type: "trending",
    items: [{ id: "e1", name: "GitHub Sync", icon: "🐙", rating: 4.8, installs: 5000 }] },
  { id: "new", title: "🆕 New Arrivals", type: "new",
    items: [{ id: "e2", name: "AI Helper", icon: "🤖" }] },
];

describe("MarketplaceHome", () => {
  it("renders the complete marketplace homepage", () => {
    const { container } = render(<MarketplaceHome featured={featured} sections={sections} />);
    expect(container.textContent).toContain("Extension Marketplace");
    expect(container.textContent).toContain("Slack Bot Pro");
    expect(container.textContent).toContain("Trending");
    expect(container.textContent).toContain("GitHub Sync");
    expect(container.textContent).toContain("New Arrivals");
    expect(container.textContent).toContain("AI Helper");
  });
});
