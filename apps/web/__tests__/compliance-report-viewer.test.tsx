import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ComplianceReportViewer } from "@/components/compliance-report-viewer";

describe("ComplianceReportViewer", () => {
  it("renders report", () => {
    const { container } = render(
      <ComplianceReportViewer framework="SOC2" organization="Acme" period="2026-Q3"
        scoreDisplay="67%" verdict="non_compliant" passed={2} failed={1}
        sections={[
          { category: "Security", count: 2, controls: [
            { id: "AC-1", name: "Access Control", status: "passed", notes: "" },
            { id: "AC-2", name: "Encryption", status: "passed", notes: "" },
          ]},
          { category: "Privacy", count: 1, controls: [
            { id: "DM-1", name: "Data Mapping", status: "failed", notes: "Incomplete" },
          ]},
        ]} />
    );
    expect(container.textContent).toContain("SOC2 Compliance Report");
    expect(container.textContent).toContain("Non-Compliant");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("Access Control");
    expect(container.textContent).toContain("Data Mapping");
    expect(container.textContent).toContain("Incomplete");
  });
});
