import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookRetryConfigCard from "../src/components/api-webhook-retry-config-card";

const configs = [
  { config_id: "c1", destination: "https://hooks.example.com", strategy: "exponential", max_attempts: 5, initial_delay_ms: 1000 },
  { config_id: "c2", destination: "https://other.com", strategy: "fixed", max_attempts: 3, initial_delay_ms: 5000 },
];

describe("APIWebhookRetryConfigCard", () => {
  it("renders header and count", () => {
    const { container } = render(<APIWebhookRetryConfigCard configs={configs} appName="App" />);
    expect(container.textContent).toContain("Retry Config");
    expect(container.textContent).toContain("2 configs");
  });

  it("shows destinations and strategies", () => {
    const { container } = render(<APIWebhookRetryConfigCard configs={configs} appName="App" />);
    expect(container.textContent).toContain("hooks.example.com");
    expect(container.textContent).toContain("exponential");
    expect(container.textContent).toContain("5 attempts");
  });

  it("shows empty state", () => {
    const { container } = render(<APIWebhookRetryConfigCard configs={[]} appName="App" />);
    expect(container.textContent).toContain("No retry configs");
  });
});
