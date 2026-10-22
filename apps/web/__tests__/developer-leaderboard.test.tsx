import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperLeaderboard } from "@/components/developer-leaderboard";

describe("DeveloperLeaderboard", () => {
  it("shows ranked devs", () => {
    const { container } = render(<DeveloperLeaderboard entries={[{ rank: 1, name: "Alice", appCount: 5, totalInstalls: 200, score: 150 }]} />);
    expect(container.textContent).toContain("#1");
    expect(container.textContent).toContain("Alice");
  });
  it("empty state", () => {
    const { container } = render(<DeveloperLeaderboard entries={[]} />);
    expect(container.textContent).toContain("No developers");
  });
});
