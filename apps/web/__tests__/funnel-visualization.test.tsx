import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FunnelVisualization } from "@/components/funnel-visualization";

describe("FunnelVisualization", () => {
  it("renders funnel", () => {
    const { container } = render(
      <FunnelVisualization overallDisplay="12.0%" worstStep="View Details"
        steps={[
          { step: "Visit Page", count: 10000, conversionDisplay: "100%", dropOff: 0, dropPct: 0 },
          { step: "View Details", count: 3000, conversionDisplay: "30%", dropOff: 7000, dropPct: 70 },
          { step: "Install", count: 1200, conversionDisplay: "12%", dropOff: 1800, dropPct: 60 },
        ]} />
    );
    expect(container.textContent).toContain("Conversion Funnel");
    expect(container.textContent).toContain("12.0% overall");
    expect(container.textContent).toContain("Visit Page");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("7,000 dropped");
    expect(container.textContent).toContain("70%");
  });
});
