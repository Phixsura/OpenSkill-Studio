import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionDiffSummary } from "@/components/version-diff-summary";

describe("VersionDiffSummary", () => {
  it("compatible", () => {
    const { container } = render(
      <VersionDiffSummary added={["version"]} removed={[]}
        modified={[{ field: "name", old_type: "str", new_type: "str", type_changed: false }]}
        totalChanges={2} breaking={false} compatible={true} />
    );
    expect(container.textContent).toContain("API Diff");
    expect(container.textContent).toContain("✅ Compatible");
    expect(container.textContent).toContain("+ version");
    expect(container.textContent).toContain("name");
  });
  it("breaking", () => {
    const { container } = render(
      <VersionDiffSummary added={[]} removed={["legacy"]}
        modified={[]} totalChanges={1} breaking={true} compatible={false} />
    );
    expect(container.textContent).toContain("⚠️ Breaking");
    expect(container.textContent).toContain("- legacy");
  });
});
