import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DevLeaderboard } from "@/components/dev-leaderboard";

describe("DevLeaderboard", () => {
  it("renders leaderboard", () => {
    const { container } = render(
      <DevLeaderboard totalDevelopers={3} leaderboard={[
        { developer: "alice", rank: 1, score: 160, commits: 50, prs: 10, reviews: 20 },
        { developer: "bob", rank: 2, score: 120, commits: 30, prs: 15, reviews: 5 },
      ]} />
    );
    expect(container.textContent).toContain("Developer Leaderboard");
    expect(container.textContent).toContain("3 developers");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("160 pts");
    expect(container.textContent).toContain("50 commits");
    expect(container.textContent).toContain("🥇");
  });
});
