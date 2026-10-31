import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookStatsCard from "../src/components/api-webhook-stats-card";

const stats = { total_sent: 9500, total_failed: 500, total_retried: 200, success_rate: 95.0, avg_latency: 120.5, p95_latency: 350.0 };

describe("APIWebhookStatsCard", () => {
  it("renders header and total", () => {
    const { container } = render(<APIWebhookStatsCard stats={stats} appName="App" />);
    expect(container.textContent).toContain("Webhook Stats");
    expect(container.textContent).toContain("10,000 deliveries");
  });

  it("shows success rate and latency", () => {
    const { container } = render(<APIWebhookStatsCard stats={stats} appName="App" />);
    expect(container.textContent).toContain("95%");
    expect(container.textContent).toContain("120.5ms");
    expect(container.textContent).toContain("350ms");
  });

  it("shows sent/failed/retried", () => {
    const { container } = render(<APIWebhookStatsCard stats={stats} appName="App" />);
    expect(container.textContent).toContain("9,500 sent");
    expect(container.textContent).toContain("500 failed");
    expect(container.textContent).toContain("200 retried");
  });
});
