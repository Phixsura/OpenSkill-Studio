import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookDeliveryMetricCard from "../src/components/api-webhook-delivery-metric-card";

const destinations = [
  { destination: "https://hooks.example.com", deliveries: 500, success_rate: 99.5, avg_latency: 120 },
  { destination: "https://slow.example.com", deliveries: 50, success_rate: 80.0, avg_latency: 2500 },
];

describe("APIWebhookDeliveryMetricCard", () => {
  it("renders header and count", () => {
    const { container } = render(<APIWebhookDeliveryMetricCard destinations={destinations} appName="App" />);
    expect(container.textContent).toContain("Delivery Metrics");
    expect(container.textContent).toContain("2 destinations");
  });

  it("shows rates and latency", () => {
    const { container } = render(<APIWebhookDeliveryMetricCard destinations={destinations} appName="App" />);
    expect(container.textContent).toContain("99.5% success");
    expect(container.textContent).toContain("120ms avg");
  });

  it("shows empty state", () => {
    const { container } = render(<APIWebhookDeliveryMetricCard destinations={[]} appName="App" />);
    expect(container.textContent).toContain("No delivery metrics");
  });
});
