import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-webhook-circuit-breaker-card";

describe("ConsumerApiWebhookCircuitBreakerCard", () => {
  it("shows breakers", () => {
    const breakers = [{ webhookId: "w1", state: "closed", failures: 2, successes: 50, threshold: 5 }];
    const { container } = render(<Card breakers={breakers} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Webhook Circuit Breakers");
    expect(container.textContent).toContain("w1");
    expect(container.textContent).toContain("closed");
    expect(container.textContent).toContain("2F / 50S");
  });
  it("shows empty", () => {
    const { container } = render(<Card breakers={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No webhook circuits");
  });
});
