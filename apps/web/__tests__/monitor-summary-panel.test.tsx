import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MonitorSummaryPanel } from "@/components/monitor-summary-panel";
describe("MonitorSummaryPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MonitorSummaryPanel score={100} status="healthy" uptimePct={99.99}
        errorRatePct={0.1} p99Ms={100} rps={5000} cpuPct={40} memoryPct={50}
        activeAlerts={0} openIncidents={0} />
    );
    expect(container.textContent).toContain("100/100");
    expect(container.textContent).toContain("HEALTHY");
    expect(container.textContent).toContain("5,000 rps");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("0.1%");
    expect(container.textContent).toContain("100ms");
  });
});
