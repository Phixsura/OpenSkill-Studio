import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DegradePolicyPanel } from "@/components/degrade-policy-panel";
describe("DegradePolicyPanel", () => {
  it("renders degraded", () => {
    const { container } = render(
      <DegradePolicyPanel activeTier="emergency" degraded={true}
        actions={["shed_all", "scale_up"]} triggeredCount={2} />
    );
    expect(container.textContent).toContain("EMERGENCY DEGRADATION");
    expect(container.textContent).toContain("2 policies");
    expect(container.textContent).toContain("shed_all");
    expect(container.textContent).toContain("scale_up");
  });
  it("renders normal", () => {
    const { container } = render(
      <DegradePolicyPanel activeTier="normal" degraded={false} actions={[]} triggeredCount={0} />
    );
    expect(container.textContent).toContain("NORMAL OPERATION");
  });
});
