import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperBadgePanel } from "@/components/developer-badge-panel";

const mockBadges = [
  { badge: "First Extension", icon: "🎯", tier: "bronze", earned: true, progress: 1, threshold: 1, percent: 100 },
  { badge: "Rising Star", icon: "⭐", tier: "silver", earned: false, progress: 50, threshold: 100, percent: 50 },
  { badge: "Marketplace Hit", icon: "🌟", tier: "gold", earned: false, progress: 200, threshold: 1000, percent: 20 },
];

describe("DeveloperBadgePanel", () => {
  it("renders badges with progress", () => {
    const { container } = render(<DeveloperBadgePanel badges={mockBadges} />);
    expect(container.textContent).toContain("First Extension");
    expect(container.textContent).toContain("1/3 earned");
    expect(container.textContent).toContain("50/100");
  });

  it("shows tier labels", () => {
    const { container } = render(<DeveloperBadgePanel badges={mockBadges} />);
    expect(container.textContent).toContain("bronze");
    expect(container.textContent).toContain("gold");
  });
});
