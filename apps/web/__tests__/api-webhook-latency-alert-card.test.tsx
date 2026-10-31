import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookLatencyAlertCard from "../src/components/api-webhook-latency-alert-card";

const alerts = [
  { alert_id: "a1", destination: "https://slow.com", threshold_ms: 500, current_avg_ms: 800, triggered: true, trigger_count: 3 },
  { alert_id: "a2", destination: "https://fast.com", threshold_ms: 500, current_avg_ms: 120, triggered: false, trigger_count: 0 },
];

describe("APIWebhookLatencyAlertCard", () => {
  it("shows alerts", () => {
    const { container } = render(<APIWebhookLatencyAlertCard alerts={alerts} appName="App" />);
    expect(container.textContent).toContain("Latency Alerts");
    expect(container.textContent).toContain("1 triggered");
    expect(container.textContent).toContain("800ms / 500ms");
  });
  it("shows empty", () => {
    const { container } = render(<APIWebhookLatencyAlertCard alerts={[]} appName="App" />);
    expect(container.textContent).toContain("No latency alerts");
  });
});
