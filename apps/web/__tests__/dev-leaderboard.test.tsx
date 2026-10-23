import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DevLeaderboard } from "@/components/dev-leaderboard";

describe("DevLeaderboard", () => {
  it("renders leaderboard", () => {
    const { container } = render(
      <DevLeaderboard period="monthly" leaderboard={[
        { name: "Carol", rank: 1, badge: "🥇", score: 275, commits: 30, pullRequests: 15, reviews: 30, deploys: 8 },
        { name: "Alice", rank: 2, badge: "🥈", score: 210, commits: 50, pullRequests: 10, reviews: 20, deploys: 5 },
      ]} />
    );
    expect(container.textContent).toContain("Developer Leaderboard");
    expect(container.textContent).toContain("monthly");
    expect(container.textContent).toContain("Carol");
    expect(container.textContent).toContain("🥇");
    expect(container.textContent).toContain("275");
    expect(container.textContent).toContain("Alice");
  });
});
