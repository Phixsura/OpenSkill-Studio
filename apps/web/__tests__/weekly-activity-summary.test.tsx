import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WeeklyActivitySummary } from "@/components/weekly-activity-summary";

describe("WeeklyActivitySummary", () => {
  const activity = { commits: 15, deploys: 3, reviews_received: 8, new_installs: 200, revenue: 500 };
  it("renders", () => {
    const { container } = render(
      <WeeklyActivitySummary developerName="Alice" week="2026-W43" activity={activity}
        activityScore={84} streakDays={5} topAchievement="📈 Growth Milestone" />
    );
    expect(container.textContent).toContain("Weekly Summary");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("84");
    expect(container.textContent).toContain("📈 Growth Milestone");
    expect(container.textContent).toContain("💻 15");
    expect(container.textContent).toContain("🔥 5-day streak");
  });
});
