import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-webhook-rate-limiter-card";

describe("WebhookRateLimiterCard", () => {
  it("shows limits", () => {
    const limits = [{ consumer_id: "c1", max_per_second: 10, max_per_minute: 100, total_limited: 5 }];
    const { container } = render(<Card limits={limits} appName="App" />);
    expect(container.textContent).toContain("Webhook Rate Limiter");
    expect(container.textContent).toContain("10/s");
    expect(container.textContent).toContain("100/min");
    expect(container.textContent).toContain("5 blocked");
  });
  it("shows empty", () => {
    const { container } = render(<Card limits={[]} appName="App" />);
    expect(container.textContent).toContain("No rate limits");
  });
});
