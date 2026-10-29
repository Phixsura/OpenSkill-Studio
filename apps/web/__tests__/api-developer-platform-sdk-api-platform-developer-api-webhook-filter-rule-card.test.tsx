import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-webhook-filter-rule-card";

describe("WebhookFilterRuleCard", () => {
  it("shows filter rules", () => {
    const rules = [{ rule_id: "r1", event_type: "order.*", action: "include", field_count: 1 }];
    const { container } = render(<Card consumerId="c1" rules={rules} totalRules={3} appName="App" />);
    expect(container.textContent).toContain("Webhook Filters");
    expect(container.textContent).toContain("order.*");
    expect(container.textContent).toContain("+1 fields");
    expect(container.textContent).toContain("3 rules");
  });
  it("shows no rules", () => {
    const { container } = render(<Card consumerId="c1" rules={[]} totalRules={0} appName="App" />);
    expect(container.textContent).toContain("No filter rules");
  });
});
