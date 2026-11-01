import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-900th-commit-milestone-card";

describe("MilestoneCard", () => {
  it("shows milestone", () => {
    const achievements = [{ milestone_id: "m-900", title: "TRANSCENDENT", tier: "transcendent", celebration_emoji: "🎊", commit_number: 900 }];
    const { container } = render(<Card commitCount={900} currentTier="transcendent" achievements={achievements} nextMilestone={1000} appName="App" />);
    expect(container.textContent).toContain("Milestone Tracker");
    expect(container.textContent).toContain("900");
    expect(container.textContent).toContain("transcendent");
    expect(container.textContent).toContain("TRANSCENDENT");
    expect(container.textContent).toContain("Next: 1000 commits");
  });
  it("shows beginner", () => {
    const { container } = render(<Card commitCount={5} currentTier="beginner" achievements={[]} nextMilestone={100} appName="App" />);
    expect(container.textContent).toContain("beginner");
  });
});
