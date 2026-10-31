import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperLeaderboardPanel } from "@/components/developer-leaderboard-panel";

const entries = [
  { rank: 1, name: "Alice", value: 10000, compositeScore: 15000 },
  { rank: 2, name: "Bob", value: 8000, compositeScore: 12000 },
  { rank: 3, name: "Charlie", value: 5000, compositeScore: 8000 },
];
const myRank = { rank: 5, total: 100, percentile: 95, score: 6000 };

describe("DeveloperLeaderboardPanel", () => {
  it("renders leaderboard with medals", () => {
    const { container } = render(<DeveloperLeaderboardPanel entries={entries} myRank={myRank} metric="installs" />);
    expect(container.textContent).toContain("🥇");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("#5");
    expect(container.textContent).toContain("Top 95%");
  });
});
