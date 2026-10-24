import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogTimeline } from "@/components/changelog-timeline";

describe("ChangelogTimeline", () => {
  const releases = [{
    version: "2.0.0", date: "2026-03-01",
    entries: [{ text: "Added dark mode", type: "feat" }, { text: "Fix login crash", type: "fix" }],
  }];
  it("renders changelog", () => {
    const { container } = render(<ChangelogTimeline releases={releases} totalEntries={2} />);
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("Added dark mode");
    expect(container.textContent).toContain("Fix login crash");
    expect(container.textContent).toContain("1 releases");
    expect(container.textContent).toContain("✨");
    expect(container.textContent).toContain("🐛");
  });
});
