import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricsExporterConfig } from "@/components/metrics-exporter-config";

describe("MetricsExporterConfig", () => {
  it("renders config", () => {
    const { container } = render(
      <MetricsExporterConfig endpoint="/metrics" scrapeIntervalSec={15}
        metrics={[
          { name: "platform_requests_total", type: "counter", value: 1000000, help: "Total requests" },
          { name: "platform_active_users", type: "gauge", value: 3200, help: "Active users" },
        ]} />
    );
    expect(container.textContent).toContain("Metrics Exporter");
    expect(container.textContent).toContain("/metrics");
    expect(container.textContent).toContain("15s");
    expect(container.textContent).toContain("platform_requests_total");
    expect(container.textContent).toContain("1,000,000");
    expect(container.textContent).toContain("counter");
  });
});
