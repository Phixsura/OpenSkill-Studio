import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-webhook-delivery-report-card";

describe("WebhookDeliveryReportCard", () => {
  it("shows report", () => {
    const periods = [{ period: "2026-06-01", total: 100, successful: 95, failed: 5, avgMs: 120, successRate: 95 }];
    const { container } = render(<Card webhookId="w1" periods={periods} overallSuccessRate={95} trend="stable" consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Delivery Report");
    expect(container.textContent).toContain("95%");
    expect(container.textContent).toContain("stable");
    expect(container.textContent).toContain("95✓");
  });
  it("shows empty", () => {
    const { container } = render(<Card webhookId="w1" periods={[]} overallSuccessRate={100} trend="stable" consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No delivery data");
  });
});
