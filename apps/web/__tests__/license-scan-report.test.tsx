import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LicenseScanReport } from "@/components/license-scan-report";

describe("LicenseScanReport", () => {
  const deps = [
    { name: "react", version: "18.3.0", license: "MIT", risk: "low", commercial: true, copyleft: false },
    { name: "gpl-lib", version: "1.0", license: "GPL-3.0", risk: "high", commercial: false, copyleft: true },
  ];
  it("renders", () => {
    const { container } = render(
      <LicenseScanReport dependencies={deps} commercialSafe={false} hasCritical={false}
        copyleftCount={1} byRisk={{ low: 1, high: 1 }} />
    );
    expect(container.textContent).toContain("License Scan");
    expect(container.textContent).toContain("⚠️ Review Required");
    expect(container.textContent).toContain("react");
    expect(container.textContent).toContain("MIT");
    expect(container.textContent).toContain("GPL-3.0");
    expect(container.textContent).toContain("Copyleft: 1");
  });
  it("safe", () => {
    const safeDeps = [deps[0]];
    const { container } = render(
      <LicenseScanReport dependencies={safeDeps} commercialSafe={true} hasCritical={false}
        copyleftCount={0} byRisk={{ low: 1 }} />
    );
    expect(container.textContent).toContain("✅ Commercial Safe");
  });
});
