import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReliabilityDashboard } from "@/components/reliability-dashboard";

describe("ReliabilityDashboard", () => {
  it("renders", () => {
    const { container } = render(
      <ReliabilityDashboard reliabilityScore={92} maturity="advanced"
        mttrMin={15} mtbfHours={720} changeFailurePct={2} uptimePct={99.95} />
    );
    expect(container.textContent).toContain("92");
    expect(container.textContent).toContain("Reliability Score");
    expect(container.textContent).toContain("advanced");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("15min");
    expect(container.textContent).toContain("720h");
  });
});
