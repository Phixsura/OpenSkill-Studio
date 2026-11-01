import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiUsageReportView } from "@/components/api-usage-report-view";

describe("ApiUsageReportView", () => {
  const endpoints = [
    { endpoint: "GET /api/apps", count: 5000, avg_latency_ms: 40, error_count: 5 },
    { endpoint: "POST /api/apps", count: 200, avg_latency_ms: 150, error_count: 0 },
  ];
  it("renders", () => {
    const { container } = render(
      <ApiUsageReportView period="Today" totalCalls={5200} successRate={99.9}
        avgLatencyMs={45} endpoints={endpoints} />
    );
    expect(container.textContent).toContain("API Usage Report");
    expect(container.textContent).toContain("5,200");
    expect(container.textContent).toContain("99.9%");
    expect(container.textContent).toContain("GET /api/apps");
    expect(container.textContent).toContain("5 errors");
  });
});
