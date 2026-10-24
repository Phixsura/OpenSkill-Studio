import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { VersionSelectorDropdown } from "@/components/version-selector-dropdown";

describe("VersionSelectorDropdown", () => {
  const versions = [
    { version: "2.0.0", publishedAt: "2026-03-01", isCurrent: true, isPrerelease: false, compatible: true, downloads: 2000 },
    { version: "1.0.0", publishedAt: "2026-01-01", isCurrent: false, isPrerelease: false, compatible: true, downloads: 5000 },
  ];
  it("renders selector", () => {
    const { container } = render(
      <VersionSelectorDropdown versions={versions} current="2.0.0" latestStable="2.0.0" onSelect={vi.fn()} />
    );
    expect(container.querySelector("select")).toBeTruthy();
    expect(container.textContent).toContain("Version");
  });
});
