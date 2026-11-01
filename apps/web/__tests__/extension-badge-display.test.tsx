import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExtensionBadgeDisplay } from "@/components/extension-badge-display";

const mockBadges = [
  { id: "b1", name: "First Extension", icon: "🎉", tier: "bronze" as const, description: "Published first extension", earnedAt: "Oct 1" },
  { id: "b2", name: "Top Rated", icon: "⭐", tier: "gold" as const, description: "Average 4.5+ rating", earnedAt: "Oct 10" },
  { id: "b3", name: "Platinum Dev", icon: "💎", tier: "platinum" as const, description: "Platinum reputation", earnedAt: "Oct 20" },
  { id: "b4", name: "Popular", icon: "🔥", tier: "silver" as const, description: "10K+ downloads", earnedAt: "Oct 15" },
];

describe("ExtensionBadgeDisplay", () => {
  it("renders badges sorted by tier", () => {
    const { container } = render(
      <ExtensionBadgeDisplay badges={mockBadges} developerName="Alice" />
    );
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("Badges");
    expect(container.textContent).toContain("Platinum Dev");
    expect(container.textContent).toContain("Top Rated");
    expect(container.textContent).toContain("First Extension");
  });

  it("shows tier counts", () => {
    const { container } = render(
      <ExtensionBadgeDisplay badges={mockBadges} developerName="Alice" />
    );
    expect(container.textContent).toContain("1 platinum");
    expect(container.textContent).toContain("1 gold");
    expect(container.textContent).toContain("1 silver");
    expect(container.textContent).toContain("1 bronze");
  });

  it("shows earned dates when enabled", () => {
    const { container } = render(
      <ExtensionBadgeDisplay badges={mockBadges} developerName="Alice" showEarnedDate />
    );
    expect(container.textContent).toContain("Earned: Oct 1");
    expect(container.textContent).toContain("Earned: Oct 20");
  });

  it("shows empty state", () => {
    const { container } = render(
      <ExtensionBadgeDisplay badges={[]} developerName="Bob" />
    );
    expect(container.textContent).toContain("No badges earned");
  });
});
