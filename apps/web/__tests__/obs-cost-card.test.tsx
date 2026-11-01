import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ObsCostCard } from "@/components/obs-cost-card";

describe("ObsCostCard", () => {
  it("renders costs", () => {
    const { container } = render(
      <ObsCostCard metricsCost={50} logsCost={50} tracesCost={20} totalCost={120}
        display="$120.00/mo" breakdownPct={{ metrics: 42, logs: 42, traces: 16 }}
        suggestions={[{ area: "logs", action: "Reduce verbosity" }]} />
    );
    expect(container.textContent).toContain("Observability Costs");
    expect(container.textContent).toContain("$120.00/mo");
    expect(container.textContent).toContain("$50");
    expect(container.textContent).toContain("Metrics (42%)");
    expect(container.textContent).toContain("Reduce verbosity");
  });
});
