import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VulnScanResults } from "@/components/vuln-scan-results";

describe("VulnScanResults", () => {
  it("renders results", () => {
    const { container } = render(
      <VulnScanResults total={2} hasCritical={true} riskScore={5}
        bySeverity={{ critical: 1, low: 1 }}
        vulns={[
          { package_name: "lodash", cve: "CVE-2021-23337", severity: "critical", fixedIn: "4.17.21" },
          { package_name: "axios", cve: "CVE-2021-3749", severity: "low", fixedIn: "0.21.2" },
        ]} />
    );
    expect(container.textContent).toContain("Vulnerability Scan");
    expect(container.textContent).toContain("2 vulns");
    expect(container.textContent).toContain("Critical");
    expect(container.textContent).toContain("lodash");
    expect(container.textContent).toContain("CVE-2021-23337");
    expect(container.textContent).toContain("4.17.21");
  });
});
