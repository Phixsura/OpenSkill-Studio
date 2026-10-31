import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionDiffViewer } from "@/components/version-diff-viewer";

describe("VersionDiffViewer", () => {
  it("renders diff", () => {
    const { container } = render(
      <VersionDiffViewer totalChanges={3} hasBreaking={true}
        added={[{ key: "retries", value: 3 }]}
        removed={[{ key: "timeout", value: 30 }]}
        changed={[{ key: "version", old: "1.0", new: "2.0" }]} />
    );
    expect(container.textContent).toContain("Version Diff");
    expect(container.textContent).toContain("3 changes");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("retries");
    expect(container.textContent).toContain("timeout");
    expect(container.textContent).toContain("1.0");
    expect(container.textContent).toContain("2.0");
  });
});
