import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-endpoint-consumer-api-consumer-api-consumer-api-webhook-rate-limiter-card";

describe("WebhookRateLimiterCard", () => {
  it("shows configs", () => {
    const configs = [{ webhookId: "w1", maxPerSec: 10, maxPerMin: 100, maxPerHour: 1000, burst: 5, currentSec: 3, currentMin: 50 }];
    const { container } = render(<Card configs={configs} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Webhook Rate Limiter");
    expect(container.textContent).toContain("w1");
    expect(container.textContent).toContain("10/s");
    expect(container.textContent).toContain("+5 burst");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No rate limits configured");
  });
});
