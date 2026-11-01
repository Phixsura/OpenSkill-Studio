import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogDiffViewer } from "@/components/changelog-diff-viewer";

describe("ChangelogDiffViewer", () => {
  it("renders diff", () => {
    const { container } = render(
      <ChangelogDiffViewer netChange={1}
        added={[{ description: "New feature", breaking: true }, { description: "Bug fix" }]}
        removed={[{ description: "Old thing" }]} />
    );
    expect(container.textContent).toContain("Changelog Diff");
    expect(container.textContent).toContain("+2");
    expect(container.textContent).toContain("-1");
    expect(container.textContent).toContain("New feature");
    expect(container.textContent).toContain("breaking");
    expect(container.textContent).toContain("Old thing");
  });
});
