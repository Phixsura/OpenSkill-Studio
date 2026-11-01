import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookDeliveryReportCard from "../src/components/api-webhook-delivery-report-card";

const reports = [{ report_id: "r1", period: "2024-01", total_sent: 9500, total_failed: 500, success_rate: 95.0, avg_latency_ms: 120 }];

describe("APIWebhookDeliveryReportCard", () => {
  it("shows reports", () => {
    const { container } = render(<APIWebhookDeliveryReportCard reports={reports} appName="App" />);
    expect(container.textContent).toContain("Delivery Reports");
    expect(container.textContent).toContain("2024-01");
    expect(container.textContent).toContain("9,500 sent");
    expect(container.textContent).toContain("95%");
  });
  it("shows empty", () => {
    const { container } = render(<APIWebhookDeliveryReportCard reports={[]} appName="App" />);
    expect(container.textContent).toContain("No delivery reports");
  });
});
