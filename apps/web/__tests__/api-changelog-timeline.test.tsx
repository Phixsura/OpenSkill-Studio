import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiChangelogTimeline } from "@/components/api-changelog-timeline";

describe("ApiChangelogTimeline", () => {
  it("renders", () => {
    const entries = [
      { version: "v3", date: "2026-10", added: 5, removed: 1, modified: 2, breaking: true, total_changes: 8 },
      { version: "v2", date: "2026-06", added: 10, removed: 0, modified: 3, breaking: false, total_changes: 13 },
    ];
    const { container } = render(<ApiChangelogTimeline entries={entries} stabilityScore={85} />);
    expect(container.textContent).toContain("API Changelog");
    expect(container.textContent).toContain("v3");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("+5 added");
    expect(container.textContent).toContain("85");
  });
});
