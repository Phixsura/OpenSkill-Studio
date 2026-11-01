import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TelemetryFunnelChart } from "@/components/telemetry-funnel-chart";

describe("TelemetryFunnelChart", () => {
  it("renders funnel", () => {
    const steps = [
      { step: "View", count: 1000, conversion_pct: 100 },
      { step: "Click", count: 300, conversion_pct: 30 },
      { step: "Install", count: 100, conversion_pct: 33.3 },
    ];
    const { container } = render(<TelemetryFunnelChart steps={steps} overallPct={10} />);
    expect(container.textContent).toContain("View");
    expect(container.textContent).toContain("1,000");
    expect(container.textContent).toContain("10% overall");
  });
});
