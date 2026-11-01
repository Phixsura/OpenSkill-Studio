import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SlaComplianceCard } from "@/components/sla-compliance-card";

describe("SlaComplianceCard", () => {
  it("renders SLAs", () => {
    const { container } = render(
      <SlaComplianceCard compliancePct={67} breachedNames={["Latency"]}
        results={[
          { name: "Uptime", target: 99.9, actual: 99.95, met: true, status: "met" },
          { name: "Latency", target: 99.0, actual: 95.0, met: false, status: "breached" },
        ]} />
    );
    expect(container.textContent).toContain("SLA Compliance");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("1 breached");
    expect(container.textContent).toContain("Uptime");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("Latency");
  });
});
