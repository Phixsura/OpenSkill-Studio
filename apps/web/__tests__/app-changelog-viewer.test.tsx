import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppChangelogViewer } from "@/components/app-changelog-viewer";

describe("AppChangelogViewer", () => {
  const releases = [{
    version: "2.0.0", date: "2026-03-01", entryCount: 2, hasBreaking: true,
    entries: [{ type: "added", text: "Dark mode" }, { type: "breaking", text: "Removed v1" }],
  }];
  it("renders changelog", () => {
    const { container } = render(
      <AppChangelogViewer appName="SuperApp" releases={releases} totalChanges={2} />
    );
    expect(container.textContent).toContain("SuperApp Changelog");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("Removed v1");
    expect(container.textContent).toContain("Breaking");
  });
});
