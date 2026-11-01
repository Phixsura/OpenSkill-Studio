import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthTrendPanel } from "@/components/health-trend-panel";
describe("HealthTrendPanel", () => {
  it("renders", () => {
    const { container } = render(
      <HealthTrendPanel trend="improving" avgUptime={99.5} recentAvg={99.9}
        worst={98} best={99.99} onTrack={true} slaTarget={99.9} risk="low" />
    );
    expect(container.textContent).toContain("Health Trend");
    expect(container.textContent).toContain("improving");
    expect(container.textContent).toContain("99.5%");
    expect(container.textContent).toContain("99.9%");
    expect(container.textContent).toContain("98%");
    expect(container.textContent).toContain("SLA 99.9%");
  });
});
