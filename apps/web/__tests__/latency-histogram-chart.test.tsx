import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LatencyHistogramChart } from "@/components/latency-histogram-chart";

describe("LatencyHistogramChart", () => {
  const histogram = [
    { le: 50, count: 100, pct: 50 },
    { le: 100, count: 60, pct: 30 },
    { le: 500, count: 40, pct: 20 },
  ];
  it("renders", () => {
    const { container } = render(
      <LatencyHistogramChart histogram={histogram} total={200} avgMs={85}
        p50Ms={45} p99Ms={450} />
    );
    expect(container.textContent).toContain("Latency Distribution");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("85ms");
    expect(container.textContent).toContain("45ms");
    expect(container.textContent).toContain("450ms");
  });
});
