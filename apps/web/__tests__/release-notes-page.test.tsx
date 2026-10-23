import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReleaseNotesPage } from "@/components/release-notes-page";

describe("ReleaseNotesPage", () => {
  it("renders notes", () => {
    const { container } = render(
      <ReleaseNotesPage version="3.2.0" date="2026-10-24" totalCommits={5} hasBreaking={false}
        sections={[
          { category: "feat", label: "✨ New Features", count: 2,
            items: [{ scope: "auth", message: "add SSO" }, { scope: "", message: "export endpoint" }] },
          { category: "fix", label: "🐛 Bug Fixes", count: 1,
            items: [{ scope: "ui", message: "button fix" }] },
        ]} />
    );
    expect(container.textContent).toContain("v3.2.0");
    expect(container.textContent).toContain("5 commits");
    expect(container.textContent).toContain("New Features (2)");
    expect(container.textContent).toContain("add SSO");
    expect(container.textContent).toContain("Bug Fixes (1)");
  });
});
