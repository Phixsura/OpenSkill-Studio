import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformWebhookConsumerBackpressureCard from "../src/components/api-developer-platform-sdk-api-platform-webhook-consumer-backpressure-card";

const states = [{ destination: "https://api.example.com", queue_depth: 5000, processing_rate_per_sec: 50, pressure_level: "high", estimated_drain_seconds: 100, rejection_count: 20 }];

describe("Card", () => {
  it("shows backpressure", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformWebhookConsumerBackpressureCard states={states} underPressureCount={1} appName="App" />);
    expect(container.textContent).toContain("Backpressure");
    expect(container.textContent).toContain("1 under pressure");
    expect(container.textContent).toContain("high");
    expect(container.textContent).toContain("5000 queued");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformWebhookConsumerBackpressureCard states={[]} underPressureCount={0} appName="App" />);
    expect(container.textContent).toContain("No backpressure data");
  });
});
