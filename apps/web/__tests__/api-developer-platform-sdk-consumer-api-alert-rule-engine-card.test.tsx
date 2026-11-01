import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-alert-rule-engine-card";

describe("AlertRuleEngineCard", () => {
  it("shows rules and alerts", () => {
    const rules = [{ id: "r1", name: "High Errors", severity: "critical", conditions: [{ metric: "error_rate", operator: "gt", threshold: 5 }], enabled: true }];
    const alerts = [{ ruleId: "r1", ruleName: "High Errors", severity: "critical", conditionsMet: ["error_rate gt 5"], timestamp: "12:00" }];
    const { container } = render(<Card rules={rules} recentAlerts={alerts} appName="App" />);
    expect(container.textContent).toContain("Alert Rules");
    expect(container.textContent).toContain("High Errors");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("error_rate gt 5");
  });
  it("shows empty", () => {
    const { container } = render(<Card rules={[]} recentAlerts={[]} appName="App" />);
    expect(container.textContent).toContain("No alert rules");
  });
});
