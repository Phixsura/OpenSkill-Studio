import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionDiffViewer } from "@/components/version-diff-viewer";

describe("VersionDiffViewer", () => {
  it("shows diff", () => {
    const { container } = render(
      <VersionDiffViewer fromVersion="1.0" toVersion="2.0" hasBreaking={true}
        permissions={{ added: ["admin"], removed: ["write"] }}
        endpoints={{ added: ["/orgs"], removed: [] }}
        config={{ added: [], removed: [] }} />
    );
    expect(container.textContent).toContain("1.0 → 2.0");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("+ admin");
    expect(container.textContent).toContain("- write");
  });
});
