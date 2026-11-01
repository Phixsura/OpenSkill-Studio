import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookHealthDashboardCard from "../src/components/api-webhook-health-dashboard-card";

const health = { total_destinations: 10, healthy_count: 8, degraded_count: 1, down_count: 1, success_rate: 95.0, avg_latency_ms: 120, circuit_breakers_open: 0, dead_letter_count: 5, overall_status: "critical" };

describe("APIWebhookHealthDashboardCard", () => {
  it("shows health", () => {
    const { container } = render(<APIWebhookHealthDashboardCard health={health} appName="App" />);
    expect(container.textContent).toContain("Webhook Health");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("95%");
    expect(container.textContent).toContain("120ms");
  });
});
