import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformChangelogPage } from "@/components/platform-changelog-page";

describe("PlatformChangelogPage", () => {
  const sections = [{
    service: "API", count: 2,
    entries: [
      { title: "New endpoint", type: "added", date: "2026-10-01", icon: "✨" },
      { title: "Fixed auth", type: "fixed", date: "2026-10-02", icon: "🐛" },
    ],
  }];
  it("renders changelog", () => {
    const { container } = render(
      <PlatformChangelogPage sections={sections} totalEntries={2} serviceCount={1} period="30d" />
    );
    expect(container.textContent).toContain("Platform Changelog");
    expect(container.textContent).toContain("API (2)");
    expect(container.textContent).toContain("New endpoint");
    expect(container.textContent).toContain("Fixed auth");
  });
});
