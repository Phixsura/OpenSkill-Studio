import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ComplianceReportCard } from "@/components/compliance-report-card";

describe("ComplianceReportCard", () => {
  it("renders report", () => {
    const { container } = render(
      <ComplianceReportCard reportId="RPT-123" framework="SOC2" score={67}
        passed={2} failed={1} compliant={false}
        controls={[
          { id: "CC1", title: "Encryption", status: "passed" },
          { id: "CC3", title: "Logging", status: "failed" },
        ]} />
    );
    expect(container.textContent).toContain("SOC2 Report");
    expect(container.textContent).toContain("RPT-123");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("Encryption");
    expect(container.textContent).toContain("Logging");
  });
});
