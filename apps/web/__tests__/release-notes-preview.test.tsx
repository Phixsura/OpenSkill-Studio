import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReleaseNotesPreview } from "@/components/release-notes-preview";

describe("ReleaseNotesPreview", () => {
  it("renders notes", () => {
    const sections = [
      { title: "✨ New Features", items: ["Dark mode", "API v2"] },
      { title: "🐛 Bug Fixes", items: ["Login crash"] },
    ];
    const { container } = render(<ReleaseNotesPreview version="2.0.0" sections={sections} totalCommits={15} />);
    expect(container.textContent).toContain("Release 2.0.0");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("15 commits");
  });
});
