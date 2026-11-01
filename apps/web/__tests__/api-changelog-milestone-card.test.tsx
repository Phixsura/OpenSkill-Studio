import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIChangelogMilestoneCard from "../src/components/api-changelog-milestone-card";

const milestones = [
  { milestone_id: "m1", title: "GA Release", version: "v1.0", pinned: true },
  { milestone_id: "m2", title: "Beta", version: "v0.9", pinned: false },
];

describe("APIChangelogMilestoneCard", () => {
  it("renders header", () => {
    const { container } = render(<APIChangelogMilestoneCard milestones={milestones} appName="App" />);
    expect(container.textContent).toContain("Milestones");
    expect(container.textContent).toContain("1 pinned / 2 total");
  });
  it("shows milestones", () => {
    const { container } = render(<APIChangelogMilestoneCard milestones={milestones} appName="App" />);
    expect(container.textContent).toContain("GA Release");
    expect(container.textContent).toContain("v1.0");
  });
  it("shows empty", () => {
    const { container } = render(<APIChangelogMilestoneCard milestones={[]} appName="App" />);
    expect(container.textContent).toContain("No milestones");
  });
});
