import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookAnalyticsPage } from "@/components/webhook-analytics-page";

describe("WebhookAnalyticsPage", () => {
  const events = [{ event: "app.installed", total: 100, success: 98, failed: 2, successRate: 98, avgLatencyMs: 55 }];
  it("renders analytics", () => {
    const { container } = render(
      <WebhookAnalyticsPage events={events} totalDeliveries={100} overallSuccessRate={98} period="7d" />
    );
    expect(container.textContent).toContain("Webhook Analytics");
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("98%");
    expect(container.textContent).toContain("100 deliveries");
  });
});
