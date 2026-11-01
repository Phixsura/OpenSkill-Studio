import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SbomViewer } from "@/components/sbom-viewer";

describe("SbomViewer", () => {
  it("renders SBOM", () => {
    const { container } = render(
      <SbomViewer appName="my-app" totalComponents={3} uniqueLicenses={["MIT", "GPL-3.0"]}
        compliant={false} violationCount={1}
        components={[
          { name: "react", version: "18.2.0", license: "MIT", type: "library" },
          { name: "custom", version: "1.0", license: "GPL-3.0", type: "library" },
        ]} />
    );
    expect(container.textContent).toContain("SBOM: my-app");
    expect(container.textContent).toContain("3 components");
    expect(container.textContent).toContain("2 licenses");
    expect(container.textContent).toContain("1 violations");
    expect(container.textContent).toContain("react");
    expect(container.textContent).toContain("MIT");
  });
});
