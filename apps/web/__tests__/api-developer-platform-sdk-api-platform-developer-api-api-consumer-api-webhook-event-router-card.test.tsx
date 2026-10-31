import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-webhook-event-router-card";

describe("WebhookEventRouterCard", () => {
  it("shows routes", () => {
    const configs = [{ consumer_id: "c1", rules: [{ rule_id: "r1", event_pattern: "order.*", target_url: "https://orders.example.com/hook", priority: 1 }], default_url: "" }];
    const { container } = render(<Card configs={configs} totalRules={1} appName="App" />);
    expect(container.textContent).toContain("Event Router");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("order.*");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} totalRules={0} appName="App" />);
    expect(container.textContent).toContain("No routing configs");
  });
});
