import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SlaComplianceDashboard } from "@/components/sla-compliance-dashboard";

describe("SlaComplianceDashboard", () => {
  const services = [
    { service: "API", compliant: true, overall_score: 100,
      metrics: [{ metric: "uptime", target: 99.9, actual: 99.95, met: true }] },
    { service: "CDN", compliant: false, overall_score: 0,
      metrics: [{ metric: "uptime", target: 99.9, actual: 99.0, met: false }] },
  ];
  it("renders", () => {
    const { container } = render(
      <SlaComplianceDashboard period="2026-Q3" services={services} complianceRate={50} />
    );
    expect(container.textContent).toContain("SLA Compliance");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Compliant");
    expect(container.textContent).toContain("Violated");
    expect(container.textContent).toContain("2026-Q3");
  });
});
