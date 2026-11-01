import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LicenseAudit } from "@/components/license-audit";

describe("LicenseAudit", () => {
  const deps = [
    { package: "react", license: "MIT", permissive: true, copyleft: false, risk: "low" },
    { package: "linux-lib", license: "GPL-3.0", permissive: false, copyleft: true, risk: "high" },
  ];
  it("renders audit", () => {
    const { container } = render(
      <LicenseAudit dependencies={deps} overallRisk="high" hasCopyleft={true} risks={{ low: 1, high: 1 }} />
    );
    expect(container.textContent).toContain("react");
    expect(container.textContent).toContain("MIT");
    expect(container.textContent).toContain("GPL-3.0");
    expect(container.textContent).toContain("copyleft");
    expect(container.textContent).toContain("high risk");
  });
});
