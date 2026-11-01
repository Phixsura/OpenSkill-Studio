import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-webhook-event-priority-card";

describe("WebhookEventPriorityCard", () => {
  it("shows rules", () => {
    const rules = [{ rule_id: "r1", event_pattern: "payment.failed", priority: 1 }];
    const { container } = render(<Card consumerId="c1" rules={rules} appName="App" />);
    expect(container.textContent).toContain("Event Priority");
    expect(container.textContent).toContain("payment.failed");
    expect(container.textContent).toContain("Critical");
  });
  it("shows empty", () => {
    const { container } = render(<Card consumerId="c1" rules={[]} appName="App" />);
    expect(container.textContent).toContain("No priority rules");
  });
});
