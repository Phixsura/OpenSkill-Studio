import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionHistoryList } from "@/components/version-history-list";

describe("VersionHistoryList", () => {
  const versions = [
    { version: "2.0.0", publishedAt: "2026-03-01", author: "Bob", changeCount: 12, downloads: 500, isLatest: true, isPrerelease: false },
    { version: "1.0.0", publishedAt: "2026-01-01", author: "Alice", changeCount: 5, downloads: 1000, isLatest: false, isPrerelease: false },
  ];
  it("renders versions", () => {
    const { container } = render(<VersionHistoryList versions={versions} latest="2.0.0" />);
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("v1.0.0");
    expect(container.textContent).toContain("Latest");
    expect(container.textContent).toContain("12 changes");
    expect(container.textContent).toContain("by Bob");
  });
});
