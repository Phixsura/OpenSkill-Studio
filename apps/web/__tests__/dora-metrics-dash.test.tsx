import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DoraMetricsDash } from "@/components/dora-metrics-dash";

describe("DoraMetricsDash", () => {
  it("renders", () => {
    const { container } = render(
      <DoraMetricsDash overall="elite"
        deployFrequency={{ value: 5, level: "elite" }}
        leadTime={{ value: 2, level: "elite" }}
        mttr={{ value: 0.5, level: "elite" }}
        changeFailureRate={{ value: 2, level: "elite" }} />
    );
    expect(container.textContent).toContain("DORA Metrics");
    expect(container.textContent).toContain("elite");
    expect(container.textContent).toContain("5/day");
    expect(container.textContent).toContain("2h");
    expect(container.textContent).toContain("0.5h");
    expect(container.textContent).toContain("2%");
  });
});
