import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CompatibilityBadge, CompatibilityMatrix } from "@/components/compatibility-badge";

describe("CompatibilityBadge", () => {
  it("renders badge", () => {
    const { container } = render(<CompatibilityBadge compat={{ extensionVersion: "1.0", platformVersion: "4.0", status: "compatible" }} />);
    expect(container.textContent).toContain("Compatible");
    expect(container.textContent).toContain("v1.0 on v4.0");
  });
});

describe("CompatibilityMatrix", () => {
  it("renders matrix", () => {
    const entries = [
      { extensionVersion: "1.0", platformVersion: "4.0", status: "compatible" },
      { extensionVersion: "1.0", platformVersion: "5.0", status: "incompatible" },
    ];
    const { container } = render(<CompatibilityMatrix entries={entries} />);
    expect(container.textContent).toContain("v1.0");
    expect(container.textContent).toContain("v4.0");
  });
});
