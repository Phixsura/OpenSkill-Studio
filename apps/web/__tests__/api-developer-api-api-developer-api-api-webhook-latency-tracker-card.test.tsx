import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiWebhookLatencyTrackerCard from "../src/components/api-developer-api-api-developer-api-api-webhook-latency-tracker-card";

const stats = [{ destination: "https://api.example.com", count: 5000, avg_ms: 45, p50_ms: 40, p99_ms: 200 }];

describe("Card", () => {
  it("shows latency", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookLatencyTrackerCard stats={stats} appName="App" />);
    expect(container.textContent).toContain("Webhook Latency");
    expect(container.textContent).toContain("45ms");
    expect(container.textContent).toContain("40ms");
    expect(container.textContent).toContain("200ms");
    expect(container.textContent).toContain("5000 deliveries");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookLatencyTrackerCard stats={[]} appName="App" />);
    expect(container.textContent).toContain("No latency data");
  });
});
