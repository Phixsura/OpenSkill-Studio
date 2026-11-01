import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookCircuitBreakerCard from "../src/components/api-webhook-circuit-breaker-card";

const breakers = [
  { destination: "https://healthy.com", state: "closed" as const, consecutive_failures: 0, failure_threshold: 5 },
  { destination: "https://failing.com", state: "open" as const, consecutive_failures: 5, failure_threshold: 5 },
];

describe("APIWebhookCircuitBreakerCard", () => {
  it("renders header and open count", () => {
    const { container } = render(<APIWebhookCircuitBreakerCard breakers={breakers} appName="App" />);
    expect(container.textContent).toContain("Webhook Breakers");
    expect(container.textContent).toContain("1 open");
  });

  it("shows states and failures", () => {
    const { container } = render(<APIWebhookCircuitBreakerCard breakers={breakers} appName="App" />);
    expect(container.textContent).toContain("closed");
    expect(container.textContent).toContain("open");
    expect(container.textContent).toContain("5/5");
  });

  it("shows empty state", () => {
    const { container } = render(<APIWebhookCircuitBreakerCard breakers={[]} appName="App" />);
    expect(container.textContent).toContain("No circuit breakers");
  });
});
