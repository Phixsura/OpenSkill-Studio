import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-usage-report-card";

describe("ConsumerApiUsageReportCard", () => {
  it("shows reports", () => {
    const reports = [{ id: "r1", period: "2026-06", metrics: [{ metric: "api_calls", value: 10000, unit: "requests", changePct: 15 }], costCents: 4999, status: "generated" }];
    const { container } = render(<Card reports={reports} consumerId="c1" totalCostCents={9998} appName="App" />);
    expect(container.textContent).toContain("Usage Reports");
    expect(container.textContent).toContain("2026-06");
    expect(container.textContent).toContain("$49.99");
    expect(container.textContent).toContain("+15%");
    expect(container.textContent).toContain("$99.98");
  });
  it("shows empty", () => {
    const { container } = render(<Card reports={[]} consumerId="c1" totalCostCents={0} appName="App" />);
    expect(container.textContent).toContain("No reports");
  });
});
