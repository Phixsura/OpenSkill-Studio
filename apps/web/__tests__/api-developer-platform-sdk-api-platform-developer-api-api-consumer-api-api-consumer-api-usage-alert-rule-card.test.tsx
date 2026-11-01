import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-usage-alert-rule-card";

describe("ConsumerApiUsageAlertRuleCard", () => {
  it("shows rules", () => {
    const rules = [{ rule_id: "r1", consumer_id: "c1", metric: "error_rate", condition: "gt", threshold: 5, severity: "critical", fired_count: 3 }];
    const { container } = render(<Card rules={rules} appName="App" />);
    expect(container.textContent).toContain("Alert Rules");
    expect(container.textContent).toContain("error_rate");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("3×");
  });
  it("shows empty", () => {
    const { container } = render(<Card rules={[]} appName="App" />);
    expect(container.textContent).toContain("No alert rules");
  });
});
