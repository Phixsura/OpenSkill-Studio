import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIWebhookSummaryReportCard from "../src/components/api-developer-api-webhook-summary-report-card";
const reports = [{ report_id: "r1", period: "2024-01", total_events: 10000, total_deliveries: 9500, success_rate: 95, avg_latency_ms: 120, top_event: "push" }];
describe("APIDeveloperAPIWebhookSummaryReportCard", () => {
  it("shows reports", () => {
    const { container } = render(<APIDeveloperAPIWebhookSummaryReportCard reports={reports} appName="App" />);
    expect(container.textContent).toContain("Webhook Reports");
    expect(container.textContent).toContain("2024-01");
    expect(container.textContent).toContain("9,500 delivered");
    expect(container.textContent).toContain("95%");
  });
});
