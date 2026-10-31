import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogTimelineCard from "../src/components/changelog-timeline-card";

const milestones = [
  { milestone_id: "m1", title: "v2.0 Release", milestone_type: "release" as const, version: "v2.0" },
  { milestone_id: "m2", title: "Dark mode", milestone_type: "feature" as const, version: "" },
  { milestone_id: "m3", title: "Login fix", milestone_type: "fix" as const, version: "v1.5.1" },
];

describe("ChangelogTimelineCard", () => {
  it("renders header and count", () => {
    const { container } = render(<ChangelogTimelineCard milestones={milestones} totalCount={10} appName="App" />);
    expect(container.textContent).toContain("Changelog Timeline");
    expect(container.textContent).toContain("10 milestones");
  });

  it("shows milestone titles with icons", () => {
    const { container } = render(<ChangelogTimelineCard milestones={milestones} totalCount={3} appName="App" />);
    expect(container.textContent).toContain("v2.0 Release");
    expect(container.textContent).toContain("🚀");
    expect(container.textContent).toContain("✨");
  });

  it("shows version badges", () => {
    const { container } = render(<ChangelogTimelineCard milestones={milestones} totalCount={3} appName="App" />);
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("v1.5.1");
  });

  it("shows empty state", () => {
    const { container } = render(<ChangelogTimelineCard milestones={[]} totalCount={0} appName="App" />);
    expect(container.textContent).toContain("No milestones");
  });
});
