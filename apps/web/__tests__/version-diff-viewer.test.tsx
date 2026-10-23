import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionDiffViewer } from "@/components/version-diff-viewer";

describe("VersionDiffViewer", () => {
  it("renders diff", () => {
    const { container } = render(
      <VersionDiffViewer addedFields={["icon"]} removedFields={["category"]}
        modifiedFields={[{ field: "version", old: "1.0", new: "2.0" }]}
        totalChanges={3} hasBreaking={true} />
    );
    expect(container.textContent).toContain("Version Diff");
    expect(container.textContent).toContain("3 changes");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("+ icon");
    expect(container.textContent).toContain("- category");
    expect(container.textContent).toContain("1.0 → 2.0");
  });
  it("no changes", () => {
    const { container } = render(
      <VersionDiffViewer addedFields={[]} removedFields={[]} modifiedFields={[]}
        totalChanges={0} hasBreaking={false} />
    );
    expect(container.textContent).toContain("No changes");
  });
});
