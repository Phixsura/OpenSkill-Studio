import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DoraMetricsPanel } from "@/components/dora-metrics-panel";
describe("DoraMetricsPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DoraMetricsPanel overall="elite"
        metrics={[
          { label: "Deploy Freq", value: "2/day", level: "elite" },
          { label: "Lead Time", value: "0.5h", level: "elite" },
          { label: "CFR", value: "2%", level: "elite" },
          { label: "MTTR", value: "0.5h", level: "elite" },
        ]} />
    );
    expect(container.textContent).toContain("DORA Metrics");
    expect(container.textContent).toContain("elite performer");
    expect(container.textContent).toContain("Deploy Freq");
    expect(container.textContent).toContain("2/day");
    expect(container.textContent).toContain("MTTR");
    expect(container.textContent).toContain("0.5h");
  });
});
