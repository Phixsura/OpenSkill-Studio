import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperWebhookDashboardCard from "../src/components/api-developer-webhook-dashboard-card";

const dash = { total_destinations: 10, active_subscriptions: 25, total_delivered: 50000, total_failed: 500, dead_letter_count: 3, circuit_breakers_open: 0, avg_delivery_ms: 120, success_rate: 99.0 };

describe("APIDeveloperWebhookDashboardCard", () => {
  it("shows all metrics", () => {
    const { container } = render(<APIDeveloperWebhookDashboardCard dashboard={dash} appName="App" />);
    expect(container.textContent).toContain("Webhook Dashboard");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("99%");
    expect(container.textContent).toContain("120ms");
  });
});
