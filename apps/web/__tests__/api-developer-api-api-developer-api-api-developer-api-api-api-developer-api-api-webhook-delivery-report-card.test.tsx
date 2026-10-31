import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiWebhookDeliveryReportCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-api-developer-api-api-webhook-delivery-report-card";

const reports = [{ report_id: "r1", period: "2025-01", total_deliveries: 50000, success_rate: 99.5, health_status: "excellent", avg_latency_ms: 45, destinations_count: 15 }];

describe("Card", () => {
  it("shows delivery reports", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiWebhookDeliveryReportCard reports={reports} appName="App" />);
    expect(container.textContent).toContain("Delivery Reports");
    expect(container.textContent).toContain("2025-01");
    expect(container.textContent).toContain("99.5%");
    expect(container.textContent).toContain("excellent");
    expect(container.textContent).toContain("50,000 total");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiWebhookDeliveryReportCard reports={[]} appName="App" />);
    expect(container.textContent).toContain("No delivery reports");
  });
});
