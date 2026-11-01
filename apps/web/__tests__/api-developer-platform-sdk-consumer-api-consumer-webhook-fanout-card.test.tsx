import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-webhook-fanout-card";

describe("ConsumerWebhookFanoutCard", () => {
  it("shows targets", () => {
    const targets = [{ id: "t1", url: "https://hook.example.com/events", active: true, filterEvents: ["order.created"] }];
    const { container } = render(<Card targets={targets} maxTargets={10} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Webhook Fanout");
    expect(container.textContent).toContain("hook.example.com");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("1/10");
  });
  it("shows empty", () => {
    const { container } = render(<Card targets={[]} maxTargets={10} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No fanout targets");
  });
});
