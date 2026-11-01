import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperLeaderboardTable } from "@/components/developer-leaderboard-table";

describe("DeveloperLeaderboardTable", () => {
  const entries = [
    { rank: 1, developer_id: "d1", display_name: "Alice", value: 8000, change: 500 },
    { rank: 2, developer_id: "d2", display_name: "Bob", value: 5000, change: -200 },
    { rank: 3, developer_id: "d3", display_name: "Carol", value: 3000, change: 0 },
  ];
  it("renders", () => {
    const { container } = render(
      <DeveloperLeaderboardTable metric="installs" period="all_time" entries={entries} />
    );
    expect(container.textContent).toContain("Leaderboard");
    expect(container.textContent).toContain("🥇");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("8,000");
    expect(container.textContent).toContain("🥈");
    expect(container.textContent).toContain("↑500");
    expect(container.textContent).toContain("↓200");
  });
});
