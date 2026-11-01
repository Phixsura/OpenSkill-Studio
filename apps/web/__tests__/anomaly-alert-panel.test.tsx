import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnomalyAlertPanel } from "@/components/anomaly-alert-panel";
describe("AnomalyAlertPanel", () => {
  it("renders", () => {
    const { container } = render(
      <AnomalyAlertPanel activeCount={2} totalFired={10}
        alerts={[
          { name: "high_cpu", metric: "cpu_pct", value: 95, threshold: 80, severity: "critical" },
          { name: "err_spike", metric: "error_rate", value: 10, threshold: 1, severity: "warning" },
        ]} />
    );
    expect(container.textContent).toContain("Anomaly Alerts");
    expect(container.textContent).toContain("2 active");
    expect(container.textContent).toContain("10 total");
    expect(container.textContent).toContain("high_cpu");
    expect(container.textContent).toContain("cpu_pct: 95");
  });
});
