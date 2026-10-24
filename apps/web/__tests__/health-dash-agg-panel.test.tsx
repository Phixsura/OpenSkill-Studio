import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthDashAggPanel } from "@/components/health-dash-agg-panel";
describe("HealthDashAggPanel", () => {
  it("renders", () => {
    const { container } = render(
      <HealthDashAggPanel status="healthy" score={100} passing={5} totalChecks={5}
        checks={{ uptime: true, error_rate: true, latency: true, saturation: true, dependencies: true }} />
    );
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("HEALTHY");
    expect(container.textContent).toContain("5/5 checks passing");
    expect(container.textContent).toContain("uptime");
    expect(container.textContent).toContain("latency");
  });
});
