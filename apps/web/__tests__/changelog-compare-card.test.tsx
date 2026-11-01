import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogCompareCard from "../src/components/changelog-compare-card";

const entries = [
  { title: "New dashboard", category: "added", breaking: false },
  { title: "Removed old API", category: "removed", breaking: true },
  { title: "Fixed login bug", category: "fixed", breaking: false },
];
const categoryCounts = { added: 1, removed: 1, fixed: 1 };

describe("ChangelogCompareCard", () => {
  it("renders header with version range", () => {
    const { container } = render(
      <ChangelogCompareCard
        fromVersion="1.0.0"
        toVersion="2.0.0"
        entries={entries}
        categoryCounts={categoryCounts}
        breakingCount={1}
        appName="My App"
      />,
    );
    expect(container.textContent).toContain("Version Compare");
    expect(container.textContent).toContain("v1.0.0 → v2.0.0");
  });

  it("shows change count", () => {
    const { container } = render(
      <ChangelogCompareCard
        fromVersion="1.0"
        toVersion="2.0"
        entries={entries}
        categoryCounts={categoryCounts}
        breakingCount={1}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("3 changes");
  });

  it("shows breaking badge", () => {
    const { container } = render(
      <ChangelogCompareCard
        fromVersion="1.0"
        toVersion="2.0"
        entries={entries}
        categoryCounts={categoryCounts}
        breakingCount={1}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("1 breaking");
  });

  it("renders entries", () => {
    const { container } = render(
      <ChangelogCompareCard
        fromVersion="1.0"
        toVersion="2.0"
        entries={entries}
        categoryCounts={categoryCounts}
        breakingCount={0}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("New dashboard");
    expect(container.textContent).toContain("Removed old API");
  });

  it("shows empty state", () => {
    const { container } = render(
      <ChangelogCompareCard
        fromVersion="1.0"
        toVersion="2.0"
        entries={[]}
        categoryCounts={{}}
        breakingCount={0}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("No changes in this range");
  });
});
