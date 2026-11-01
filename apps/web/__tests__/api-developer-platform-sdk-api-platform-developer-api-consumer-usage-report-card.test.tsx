import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-consumer-usage-report-card";

describe("UsageReportCard", () => {
  it("shows metrics", () => {
    const metrics = { total_requests: 15000, success_rate: 99.5, avg_latency_ms: 42, data_transferred_bytes: 5242880 };
    const { container } = render(<Card consumerId="c1" metrics={metrics} period="daily" appName="App" />);
    expect(container.textContent).toContain("Usage Report");
    expect(container.textContent).toContain("15,000");
    expect(container.textContent).toContain("99.5%");
    expect(container.textContent).toContain("42ms");
    expect(container.textContent).toContain("5.0 MB");
  });
  it("shows period", () => {
    const metrics = { total_requests: 0, success_rate: 0, avg_latency_ms: 0, data_transferred_bytes: 0 };
    const { container } = render(<Card consumerId="c1" metrics={metrics} period="weekly" appName="App" />);
    expect(container.textContent).toContain("weekly");
  });
});
