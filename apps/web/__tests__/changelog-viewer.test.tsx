import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogViewer } from "@/components/changelog-viewer";

describe("ChangelogViewer", () => {
  it("renders changelog", () => {
    const { container } = render(
      <ChangelogViewer version="2.0.0" commitCount={3}
        sections={{ Features: ["Dashboard", "API v2"], "Bug Fixes": ["Login bug"] }} />
    );
    expect(container.textContent).toContain("Changelog v2.0.0");
    expect(container.textContent).toContain("3 commits");
    expect(container.textContent).toContain("Features");
    expect(container.textContent).toContain("Dashboard");
    expect(container.textContent).toContain("Bug Fixes");
    expect(container.textContent).toContain("Login bug");
  });
});
