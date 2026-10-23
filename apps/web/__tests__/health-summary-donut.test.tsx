import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthSummaryDonut } from "@/components/health-summary-donut";

describe("HealthSummaryDonut", () => {
  it("renders", () => {
    const signals = { uptime: 99.9, errors: 99, latency: 95, stability: 99.5, satisfaction: 90 };
    const { container } = render(
      <HealthSummaryDonut overallScore={97} status="excellent" signals={signals} />
    );
    expect(container.textContent).toContain("97");
    expect(container.textContent).toContain("excellent");
    expect(container.textContent).toContain("🟢");
    expect(container.textContent).toContain("Uptime");
    expect(container.textContent).toContain("99.9/100");
  });
});
