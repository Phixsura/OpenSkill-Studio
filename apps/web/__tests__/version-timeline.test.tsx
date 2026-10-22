import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionTimeline } from "@/components/version-timeline";

const ENTRIES = [
  { version: "2.0", date: "2026-02", status: "approved", changelog: "Big update", isLatest: true },
  { version: "1.0", date: "2026-01", status: "approved", changelog: "Initial", isLatest: false },
];

describe("VersionTimeline", () => {
  it("shows versions", () => {
    const { container } = render(<VersionTimeline entries={ENTRIES} />);
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("v1.0");
  });
  it("shows latest badge", () => {
    const { container } = render(<VersionTimeline entries={ENTRIES} />);
    expect(container.textContent).toContain("Latest");
  });
  it("empty state", () => {
    const { container } = render(<VersionTimeline entries={[]} />);
    expect(container.textContent).toContain("No versions");
  });
});
