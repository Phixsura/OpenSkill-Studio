import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AchievementBadges } from "@/components/achievement-badges";

describe("AchievementBadges", () => {
  it("renders badges", () => {
    const { container } = render(
      <AchievementBadges totalPoints={85} level={3} levelTitle="Builder" nextAt={100}
        earned={[
          { title: "App Creator", icon: "📱", description: "First app", points: 10 },
          { title: "Speed Demon", icon: "⚡", description: "Fast!", points: 35 },
        ]} />
    );
    expect(container.textContent).toContain("Achievements");
    expect(container.textContent).toContain("Level 3: Builder");
    expect(container.textContent).toContain("85 points");
    expect(container.textContent).toContain("15 to next");
    expect(container.textContent).toContain("App Creator");
    expect(container.textContent).toContain("Speed Demon");
  });
});
