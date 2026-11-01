import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InfraCostOptDash } from "@/components/infra-cost-opt-dash";

describe("InfraCostOptDash", () => {
  it("renders", () => {
    const { container } = render(
      <InfraCostOptDash totalMonthlyCost={5000} potentialSavings={1200} savingsPct={24}
        opportunities={[
          { resource: "idle-vm", type: "vm", utilizationPct: 5, monthlyCost: 100, potentialSavings: 70, recommendation: "terminate_or_downsize" },
          { resource: "low-vm", type: "vm", utilizationPct: 30, monthlyCost: 150, potentialSavings: 60, recommendation: "rightsize" },
        ]} />
    );
    expect(container.textContent).toContain("Cost Optimizer");
    expect(container.textContent).toContain("$5,000");
    expect(container.textContent).toContain("$1,200");
    expect(container.textContent).toContain("24%");
    expect(container.textContent).toContain("idle-vm");
    expect(container.textContent).toContain("terminate or downsize");
  });
});
