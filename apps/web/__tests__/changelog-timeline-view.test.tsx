import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogTimelineView } from "@/components/changelog-timeline-view";

describe("ChangelogTimelineView", () => {
  const timeline = [
    { version: "2.0.0", date: "2026-10-01", title: "Major Redesign",
      features: 2, fixes: 1, breaking: 1, total_changes: 3, is_major: true },
    { version: "1.1.0", date: "2026-09-01", title: "Minor update",
      features: 1, fixes: 1, breaking: 0, total_changes: 2, is_major: false },
  ];
  it("renders", () => {
    const { container } = render(
      <ChangelogTimelineView timeline={timeline} totalVersions={2} totalChanges={5} />
    );
    expect(container.textContent).toContain("Changelog Timeline");
    expect(container.textContent).toContain("2 versions · 5 changes");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("Major Redesign");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("✨ 2 features");
  });
});
