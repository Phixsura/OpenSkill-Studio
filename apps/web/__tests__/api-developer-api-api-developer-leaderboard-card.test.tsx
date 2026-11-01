import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperLeaderboardCard from "../src/components/api-developer-api-api-developer-leaderboard-card";

const entries = [
  { developer_id: "d1", display_name: "Alice", total_score: 1500, rank_tier: "diamond" },
  { developer_id: "d2", display_name: "Bob", total_score: 300, rank_tier: "gold" },
];

describe("APIDeveloperAPIApiDeveloperLeaderboardCard", () => {
  it("shows leaderboard", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperLeaderboardCard entries={entries} tierCounts={{ diamond: 1, gold: 1 }} appName="App" />);
    expect(container.textContent).toContain("Developer Leaderboard");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("1500");
    expect(container.textContent).toContain("#1");
    expect(container.textContent).toContain("Bob");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperLeaderboardCard entries={[]} tierCounts={{}} appName="App" />);
    expect(container.textContent).toContain("No developers");
  });
});
