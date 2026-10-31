import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-webhook-delivery-report-card";

describe("DeliveryReportCard", () => {
  it("shows report", () => {
    const metrics = { total_deliveries: 10000, successful: 9500, failed: 500, retried: 200, avg_latency_ms: 45 };
    const { container } = render(<Card period="2024-01" metrics={metrics} successRate={95} appName="App" />);
    expect(container.textContent).toContain("Delivery Report");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("9,500");
    expect(container.textContent).toContain("95%");
  });
  it("shows period", () => {
    const metrics = { total_deliveries: 0, successful: 0, failed: 0, retried: 0, avg_latency_ms: 0 };
    const { container } = render(<Card period="2024-02" metrics={metrics} successRate={0} appName="App" />);
    expect(container.textContent).toContain("2024-02");
  });
});
