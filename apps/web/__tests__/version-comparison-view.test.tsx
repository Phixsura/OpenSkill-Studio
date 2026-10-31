import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionComparisonView } from "@/components/version-comparison-view";

describe("VersionComparisonView", () => {
  it("renders comparison", () => {
    const { container } = render(
      <VersionComparisonView versionA="1.0" versionB="2.0"
        onlyInA={[]} onlyInB={[{ description: "New feature" }]} common={[]}
        permsAdded={["write"]} permsRemoved={[]} hasBreaking={false}
        migrationNotes={["Safe to update"]} />
    );
    expect(container.textContent).toContain("1.0 → 2.0");
    expect(container.textContent).toContain("New feature");
    expect(container.textContent).toContain("+ write");
    expect(container.textContent).toContain("Safe to update");
  });
  it("shows breaking", () => {
    const { container } = render(
      <VersionComparisonView versionA="1.0" versionB="2.0"
        onlyInA={[]} onlyInB={[]} common={[]} permsAdded={[]} permsRemoved={["admin"]}
        hasBreaking={true} migrationNotes={[]} />
    );
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("- admin");
  });
});
