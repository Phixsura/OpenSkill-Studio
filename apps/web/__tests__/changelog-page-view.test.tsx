import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogPageView } from "@/components/changelog-page-view";

describe("ChangelogPageView", () => {
  const releases = [{
    version: "2.0.0", date: "2026-03-01", hasBreaking: false,
    entries: [{ type: "added", text: "Dark mode", icon: "✨" }],
  }];
  it("renders changelog", () => {
    const { container } = render(
      <ChangelogPageView appName="SuperApp" releases={releases} totalEntries={1}
        availableFilters={["added", "fixed"]} onFilter={vi.fn()} />
    );
    expect(container.textContent).toContain("SuperApp Changelog");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("1 changes");
  });
});
