import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FunnelVisualization } from "@/components/funnel-visualization";

describe("FunnelVisualization", () => {
  it("renders funnel", () => {
    const { container } = render(
      <FunnelVisualization overallConversion={5} bottleneck="Signup"
        funnel={[
          { step: "Visit", count: 1000, dropOffPct: 0, conversionPct: 100 },
          { step: "Signup", count: 500, dropOffPct: 50, conversionPct: 50 },
          { step: "Subscribe", count: 50, dropOffPct: 90, conversionPct: 5 },
        ]} />
    );
    expect(container.textContent).toContain("User Funnel");
    expect(container.textContent).toContain("5% conversion");
    expect(container.textContent).toContain("bottleneck: Signup");
    expect(container.textContent).toContain("Visit");
    expect(container.textContent).toContain("1,000");
    expect(container.textContent).toContain("50% drop-off");
  });
});
