import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepSecScan } from "@/components/dep-sec-scan";

describe("DepSecScan", () => {
  it("renders", () => {
    const { container } = render(
      <DepSecScan totalDeps={10} safe={8} vulnerable={2} totalVulns={3}
        critical={1} high={1} pass={false}
        vulns={[
          { package_name: "lodash", cve: "CVE-2021-23337", severity: "critical", fixedIn: "4.17.21" },
          { package_name: "axios", cve: "CVE-2021-3749", severity: "medium", fixedIn: "" },
        ]} />
    );
    expect(container.textContent).toContain("Dependency Security");
    expect(container.textContent).toContain("3 vulns");
    expect(container.textContent).toContain("8");
    expect(container.textContent).toContain("lodash");
    expect(container.textContent).toContain("CVE-2021-23337");
    expect(container.textContent).toContain("4.17.21");
  });
});
