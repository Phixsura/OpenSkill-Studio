import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-webhook-fanout-card";

describe("WebhookFanoutCard", () => {
  it("shows targets", () => {
    const targets = [{ target_id: "t1", url: "https://hooks.example.com/wh", active: true, delivery_count: 100, failure_count: 2 }];
    const { container } = render(<Card consumerId="c1" targets={targets} maxTargets={10} appName="App" />);
    expect(container.textContent).toContain("Webhook Fanout");
    expect(container.textContent).toContain("1/10 targets");
    expect(container.textContent).toContain("hooks.example.com");
  });
  it("shows empty", () => {
    const { container } = render(<Card consumerId="c1" targets={[]} maxTargets={10} appName="App" />);
    expect(container.textContent).toContain("No fanout targets");
  });
});
