import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AutoRemediationPanel } from "@/components/auto-remediation-panel";

describe("AutoRemediationPanel", () => {
  it("renders", () => {
    const { container } = render(
      <AutoRemediationPanel autoPct={75} total={4} actions={[
        { issue: "high_cpu", action: "scale_up", description: "Add replicas", severity: "warning", autoApprove: true },
        { issue: "high_error_rate", action: "rollback", description: "Rollback deploy", severity: "critical", autoApprove: false },
      ]} />
    );
    expect(container.textContent).toContain("Auto-Remediation");
    expect(container.textContent).toContain("4 actions");
    expect(container.textContent).toContain("75% automated");
    expect(container.textContent).toContain("high_cpu");
    expect(container.textContent).toContain("scale_up");
    expect(container.textContent).toContain("auto");
    expect(container.textContent).toContain("manual");
  });
});
