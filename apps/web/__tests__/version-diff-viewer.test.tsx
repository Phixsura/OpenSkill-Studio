import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionDiffViewer } from "@/components/version-diff-viewer";

describe("VersionDiffViewer", () => {
  it("renders diff", () => {
    const { container } = render(
      <VersionDiffViewer summary="+1 -1 ~1" breaking={true}
        added={[{ method: "GET", path: "/exports" }]}
        removed={[{ method: "GET", path: "/legacy" }]}
        changed={[{ endpoint: "POST:/users" }]} />
    );
    expect(container.textContent).toContain("API Version Diff");
    expect(container.textContent).toContain("+1 -1 ~1");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("+ GET /exports");
    expect(container.textContent).toContain("- GET /legacy");
    expect(container.textContent).toContain("~ POST:/users");
  });
});
