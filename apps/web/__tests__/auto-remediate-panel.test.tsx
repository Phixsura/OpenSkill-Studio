import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AutoRemediatePanel } from "@/components/auto-remediate-panel";
describe("AutoRemediatePanel", () => {
  it("renders", () => {
    const { container } = render(
      <AutoRemediatePanel totalRules={5} actionsTaken={10}
        actions={[
          { rule: "high_cpu", severity: "critical", autoFixed: true },
          { rule: "low_disk", severity: "warning", autoFixed: true },
        ]} />
    );
    expect(container.textContent).toContain("Auto-Remediation");
    expect(container.textContent).toContain("5 rules");
    expect(container.textContent).toContain("10 actions taken");
    expect(container.textContent).toContain("high_cpu");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("fixed");
  });
});
