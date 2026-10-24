import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepVulnReport } from "@/components/dep-vuln-report";

describe("DepVulnReport", () => {
  it("renders findings", () => {
    const { container } = render(
      <DepVulnReport depsScanned={10} critical={1} high={0} clean={false}
        findings={[
          { package_name: "lodash", version: "4.17.20", cve: "CVE-2021-12345",
            severity: "critical", fixVersion: "4.17.21", title: "Prototype pollution" },
        ]} />
    );
    expect(container.textContent).toContain("Vulnerability Scan");
    expect(container.textContent).toContain("1C 0H");
    expect(container.textContent).toContain("lodash@4.17.20");
    expect(container.textContent).toContain("CVE-2021-12345");
    expect(container.textContent).toContain("fix: 4.17.21");
  });
});
