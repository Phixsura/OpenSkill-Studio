import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookRoutingRuleCard from "../src/components/api-webhook-routing-rule-card";

const rules = [
  { rule_id: "r1", event_pattern: "push", destination: "https://a.com", priority: 10, enabled: true, routed_count: 50 },
  { rule_id: "r2", event_pattern: "*", destination: "https://catch.com", priority: 1, enabled: false, routed_count: 0 },
];

describe("APIWebhookRoutingRuleCard", () => {
  it("shows rules", () => {
    const { container } = render(<APIWebhookRoutingRuleCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Routing Rules");
    expect(container.textContent).toContain("1/2 active");
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("P10");
  });
  it("shows empty", () => {
    const { container } = render(<APIWebhookRoutingRuleCard rules={[]} appName="App" />);
    expect(container.textContent).toContain("No routing rules");
  });
});
