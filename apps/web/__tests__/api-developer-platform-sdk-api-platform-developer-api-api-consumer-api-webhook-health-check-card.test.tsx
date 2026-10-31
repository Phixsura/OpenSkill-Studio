import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-webhook-health-check-card";

describe("WebhookHealthCheckCard", () => {
  it("shows health", () => {
    const endpoints = [{ endpoint: "/wh", consumer_id: "c1", healthy: true, availability: 99.5, consecutive_failures: 0 }];
    const { container } = render(<Card endpoints={endpoints} unhealthyCount={0} appName="App" />);
    expect(container.textContent).toContain("Webhook Health");
    expect(container.textContent).toContain("99.5%");
  });
  it("shows unhealthy", () => {
    const { container } = render(<Card endpoints={[]} unhealthyCount={2} appName="App" />);
    expect(container.textContent).toContain("2 down");
  });
});
