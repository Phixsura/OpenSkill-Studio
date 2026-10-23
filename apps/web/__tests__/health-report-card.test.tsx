import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthReportCard } from "@/components/health-report-card";

describe("HealthReportCard", () => {
  it("renders report", () => {
    const { container } = render(
      <HealthReportCard score={92} grade="A"
        services={{ total: 10, healthy: 9, degraded: 1, down: 0 }}
        incidents={{ total: 5, open: 1 }}
        slaCompliance={99.5} uptimePct={99.9} recommendation="No action needed" />
    );
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("92/100");
    expect(container.textContent).toContain("9/10");
    expect(container.textContent).toContain("99.9%");
    expect(container.textContent).toContain("1 open");
    expect(container.textContent).toContain("No action needed");
  });
});
