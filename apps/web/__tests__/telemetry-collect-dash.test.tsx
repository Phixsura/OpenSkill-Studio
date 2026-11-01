import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TelemetryCollectDash } from "@/components/telemetry-collect-dash";

describe("TelemetryCollectDash", () => {
  it("renders", () => {
    const { container } = render(
      <TelemetryCollectDash totalMetrics={5} counters={2} gauges={1} histograms={2}
        metrics={[
          { name: "requests", type: "counter", value: 1500 },
          { name: "cpu_pct", type: "gauge", value: 75.5 },
          { name: "latency_ms", type: "histogram", value: "p50=100ms" },
        ]} />
    );
    expect(container.textContent).toContain("Telemetry");
    expect(container.textContent).toContain("5 metrics");
    expect(container.textContent).toContain("2C 1G 2H");
    expect(container.textContent).toContain("requests");
    expect(container.textContent).toContain("counter");
    expect(container.textContent).toContain("1500");
    expect(container.textContent).toContain("cpu_pct");
  });
});
