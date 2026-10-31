import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogStatsCard from "../src/components/changelog-stats-card";

const stats = {
  total_releases: 12,
  total_entries: 85,
  breaking_changes: 3,
  avg_days_between_releases: 14.5,
  top_contributors: [
    ["alice", 8],
    ["bob", 5],
  ] as [string, number][],
  categories: { added: 40, fixed: 25, changed: 15, removed: 5 },
};

describe("ChangelogStatsCard", () => {
  it("renders header", () => {
    const { container } = render(<ChangelogStatsCard stats={stats} appName="My App" />);
    expect(container.textContent).toContain("Changelog Stats");
    expect(container.textContent).toContain("My App");
  });

  it("shows key metrics", () => {
    const { container } = render(<ChangelogStatsCard stats={stats} appName="App" />);
    expect(container.textContent).toContain("12");
    expect(container.textContent).toContain("Releases");
    expect(container.textContent).toContain("85");
    expect(container.textContent).toContain("Changes");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("Breaking");
  });

  it("shows cadence", () => {
    const { container } = render(<ChangelogStatsCard stats={stats} appName="App" />);
    expect(container.textContent).toContain("14.5d");
    expect(container.textContent).toContain("Cadence");
  });

  it("renders categories", () => {
    const { container } = render(<ChangelogStatsCard stats={stats} appName="App" />);
    expect(container.textContent).toContain("added (40)");
    expect(container.textContent).toContain("fixed (25)");
  });

  it("renders contributors", () => {
    const { container } = render(<ChangelogStatsCard stats={stats} appName="App" />);
    expect(container.textContent).toContain("alice (8)");
    expect(container.textContent).toContain("bob (5)");
  });
});
