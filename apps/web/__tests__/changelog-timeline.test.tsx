import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogTimeline } from "@/components/changelog-timeline";

describe("ChangelogTimeline", () => {
  it("renders entries", () => {
    const entries = [{
      version: "2.0.0", released_at: "2026-06-01T00:00:00Z", total_changes: 3,
      categories: { added: ["Dark mode", "API v2"], fixed: ["Login bug"] },
    }];
    const { container } = render(<ChangelogTimeline entries={entries} />);
    expect(container.textContent).toContain("2.0.0");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("3 changes");
  });
  it("empty state", () => {
    const { container } = render(<ChangelogTimeline entries={[]} />);
    expect(container.textContent).toContain("No changelog");
  });
});
