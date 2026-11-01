import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiWebhookCircuitBreakerConfigCard from "../src/components/api-developer-api-api-developer-api-api-webhook-circuit-breaker-config-card";

const configs = [{ destination: "https://api.example.com", failure_threshold: 5, recovery_timeout_seconds: 60, half_open_max_requests: 3, success_threshold: 2, enabled: true }];

describe("Card", () => {
  it("shows configs", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookCircuitBreakerConfigCard configs={configs} appName="App" />);
    expect(container.textContent).toContain("Circuit Breaker Config");
    expect(container.textContent).toContain("1/1 enabled");
    expect(container.textContent).toContain("5 fails");
    expect(container.textContent).toContain("recovery: 60s");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookCircuitBreakerConfigCard configs={[]} appName="App" />);
    expect(container.textContent).toContain("No circuit breakers");
  });
});
