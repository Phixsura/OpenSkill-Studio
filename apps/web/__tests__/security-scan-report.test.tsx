import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SecurityScanReport } from "@/components/security-scan-report";

describe("SecurityScanReport", () => {
  it("renders scan", () => {
    const { container } = render(
      <SecurityScanReport scoreDisplay="80%" status="warning" criticalFailures={0}
        results={[
          { title: "HTTPS Only", severity: "high", passed: true },
          { title: "CSP Headers", severity: "medium", passed: false },
        ]} />
    );
    expect(container.textContent).toContain("Security Scan");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("warning");
    expect(container.textContent).toContain("HTTPS Only");
    expect(container.textContent).toContain("CSP Headers");
  });
});
