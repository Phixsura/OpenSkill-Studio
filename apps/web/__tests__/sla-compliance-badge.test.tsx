import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SlaComplianceBadge } from "@/components/sla-compliance-badge";

describe("SlaComplianceBadge", () => {
  it("shows compliant", () => {
    const { container } = render(
      <SlaComplianceBadge compliant={true} checks={{ uptime: { target: 99.9, actual: 99.95, met: true } }} />
    );
    expect(container.textContent).toContain("SLA Compliant");
    expect(container.textContent).toContain("99.95");
  });
  it("shows violation", () => {
    const { container } = render(
      <SlaComplianceBadge compliant={false} checks={{ uptime: { target: 99.9, actual: 98, met: false } }} />
    );
    expect(container.textContent).toContain("SLA Violation");
  });
});
