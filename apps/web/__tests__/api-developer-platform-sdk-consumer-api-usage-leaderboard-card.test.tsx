import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import UsageLeaderboardCard from "../src/components/api-developer-platform-sdk-consumer-api-usage-leaderboard-card";

describe("UsageLeaderboardCard", () => {
  it("renders title and ranking", () => {
    const { container } = render(<UsageLeaderboardCard />);
    expect(container.textContent).toContain("Usage Leaderboard");
    expect(container.textContent).toContain("acme-corp");
    expect(container.textContent).toContain("beta-inc");
  });

  it("shows tiers and points", () => {
    const { container } = render(<UsageLeaderboardCard />);
    expect(container.textContent).toContain("platinum");
    expect(container.textContent).toContain("125,000 pts");
    expect(container.textContent).toContain("Top 3");
  });
});
