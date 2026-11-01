import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AlertRulePanel } from "@/components/alert-rule-panel";

describe("AlertRulePanel", () => {
  it("renders", () => {
    const { container } = render(
      <AlertRulePanel hasCritical={true} total={2}
        alerts={[
          { rule: "high_cpu", metric: "cpu_pct", value: 95, threshold: 80, severity: "warning" },
          { rule: "critical_cpu", metric: "cpu_pct", value: 95, threshold: 90, severity: "critical" },
        ]} />
    );
    expect(container.textContent).toContain("Alert Rules");
    expect(container.textContent).toContain("2 firing");
    expect(container.textContent).toContain("high_cpu");
    expect(container.textContent).toContain("critical");
  });
});
