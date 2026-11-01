import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-usage-leaderboard-card";

describe("UsageLeaderboardCard", () => {
  it("shows leaderboard", () => {
    const entries = [{ rank: 1, consumer_id: "c2", total_requests: 5000, success_rate: 98, score: 500 }, { rank: 2, consumer_id: "c1", total_requests: 1000, success_rate: 99, score: 200 }];
    const { container } = render(<Card entries={entries} appName="App" />);
    expect(container.textContent).toContain("Usage Leaderboard");
    expect(container.textContent).toContain("c2");
    expect(container.textContent).toContain("5,000 reqs");
  });
  it("shows empty", () => {
    const { container } = render(<Card entries={[]} appName="App" />);
    expect(container.textContent).toContain("No usage data");
  });
});
