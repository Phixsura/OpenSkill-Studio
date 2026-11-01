import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionHistoryTimeline } from "@/components/version-history-timeline";

describe("VersionHistoryTimeline", () => {
  const versions = [
    { version: "2.0.0", release_date: "2026-06-01T00:00:00", summary: "Major release", is_major: true, download_count: 5000 },
    { version: "1.1.0", release_date: "2026-03-01T00:00:00", summary: "Minor update", is_major: false, download_count: 3200 },
  ];
  it("renders timeline", () => {
    const { container } = render(<VersionHistoryTimeline appName="MyApp" versions={versions} />);
    expect(container.textContent).toContain("MyApp — Version History");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("Major release");
    expect(container.textContent).toContain("v1.1.0");
  });
});
