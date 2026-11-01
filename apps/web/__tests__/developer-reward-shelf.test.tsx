import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperRewardShelf } from "@/components/developer-reward-shelf";

describe("DeveloperRewardShelf", () => {
  const earned = [
    { id: "first_publish", name: "First Publish", icon: "🚀", xp: 100 },
    { id: "streak_7", name: "7-Day Streak", icon: "🔥", xp: 150 },
  ];
  it("renders", () => {
    const { container } = render(
      <DeveloperRewardShelf earned={earned} totalXp={250} level={1} xpToNext={250} nextLevelXp={500} />
    );
    expect(container.textContent).toContain("Rewards");
    expect(container.textContent).toContain("Level 1");
    expect(container.textContent).toContain("250 XP");
    expect(container.textContent).toContain("🚀");
    expect(container.textContent).toContain("First Publish");
    expect(container.textContent).toContain("🔥");
  });
});
