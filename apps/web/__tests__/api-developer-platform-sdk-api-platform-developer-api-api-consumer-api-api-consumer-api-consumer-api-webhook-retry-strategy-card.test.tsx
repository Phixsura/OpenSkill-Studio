import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-webhook-retry-strategy-card";

describe("WebhookRetryStrategyCard", () => {
  it("shows strategy", () => {
    const schedule = [{ attempt: 1, delaySec: 10 }, { attempt: 2, delaySec: 20 }, { attempt: 3, delaySec: 40 }];
    const { container } = render(<Card webhookId="w1" strategyType="exponential" maxRetries={5} baseDelay={10} maxDelay={3600} multiplier={2} schedule={schedule} appName="App" />);
    expect(container.textContent).toContain("Retry Strategy");
    expect(container.textContent).toContain("exponential");
    expect(container.textContent).toContain("2x");
    expect(container.textContent).toContain("#1: 10s");
    expect(container.textContent).toContain("#3: 40s");
  });
  it("shows fixed", () => {
    const { container } = render(<Card webhookId="w1" strategyType="fixed" maxRetries={3} baseDelay={60} maxDelay={60} multiplier={1} schedule={[]} appName="App" />);
    expect(container.textContent).toContain("fixed");
    expect(container.textContent).toContain("60s");
  });
});
