import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SlaComplianceCard } from "@/components/sla-compliance-card";

describe("SlaComplianceCard", () => {
  it("renders breached SLA", () => {
    const { container } = render(
      <SlaComplianceCard status="breached" scoreDisplay="25%" period="monthly" creditDue={true}
        checks={[
          { metric: "uptime", actual: 99.5, target: 99.9, unit: "%", passed: false },
          { metric: "avg_response", actual: 150, target: 200, unit: "ms", passed: true },
        ]} />
    );
    expect(container.textContent).toContain("SLA Compliance");
    expect(container.textContent).toContain("25%");
    expect(container.textContent).toContain("Uptime");
    expect(container.textContent).toContain("99.5%");
    expect(container.textContent).toContain("SLA credit due");
  });
});
