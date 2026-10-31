import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BadgeDisplay } from "@/components/badge-display";

describe("BadgeDisplay", () => {
  const badges = [
    { id: "verified", label: "Verified", icon: "✅", description: "Verified app" },
    { id: "popular", label: "Popular", icon: "🔥", description: "10K+ installs" },
  ];
  it("renders badges", () => {
    const { container } = render(<BadgeDisplay badges={badges} />);
    expect(container.textContent).toContain("Verified");
    expect(container.textContent).toContain("Popular");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("🔥");
  });
  it("hides when empty", () => {
    const { container } = render(<BadgeDisplay badges={[]} />);
    expect(container.innerHTML).toBe("");
  });
});
