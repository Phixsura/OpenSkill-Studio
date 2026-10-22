import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppVersionList } from "@/components/app-version-list";

const VERSIONS = [
  { version: "2.0.0", reviewStatus: "approved", createdAt: "2026-02" },
  { version: "1.0.0", reviewStatus: "approved", createdAt: "2026-01" },
];

describe("AppVersionList", () => {
  it("shows versions", () => {
    const { container } = render(<AppVersionList versions={VERSIONS} />);
    expect(container.textContent).toContain("2.0.0");
    expect(container.textContent).toContain("1.0.0");
  });

  it("shows review status", () => {
    const { container } = render(<AppVersionList versions={VERSIONS} />);
    expect(container.textContent).toContain("approved");
  });

  it("empty state", () => {
    const { container } = render(<AppVersionList versions={[]} />);
    expect(container.textContent).toContain("No versions");
  });
});
