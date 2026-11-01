import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReleaseNotesViewer } from "@/components/release-notes-viewer";

describe("ReleaseNotesViewer", () => {
  it("renders", () => {
    const { container } = render(
      <ReleaseNotesViewer version="2.0.0" totalCommits={4} hasBreaking={true}
        features={["feat: add dark mode", "feat: new API"]}
        fixes={["fix: login bug"]}
        breakingChanges={["feat: BREAKING CHANGE: new API"]} />
    );
    expect(container.textContent).toContain("Release Notes");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("4 commits");
    expect(container.textContent).toContain("BREAKING");
    expect(container.textContent).toContain("Features");
    expect(container.textContent).toContain("dark mode");
    expect(container.textContent).toContain("Fixes");
    expect(container.textContent).toContain("login bug");
  });
});
