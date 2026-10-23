import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LatencyPercentileChart } from "@/components/latency-percentile-chart";

describe("LatencyPercentileChart", () => {
  it("renders latency", () => {
    const { container } = render(
      <LatencyPercentileChart p50={50} p90={90} p95={95} p99={99}
        avg={55} min={1} max={100} count={1000} status="fast" />
    );
    expect(container.textContent).toContain("Latency");
    expect(container.textContent).toContain("fast");
    expect(container.textContent).toContain("p50");
    expect(container.textContent).toContain("50ms");
    expect(container.textContent).toContain("p99");
    expect(container.textContent).toContain("99ms");
    expect(container.textContent).toContain("1,000 samples");
  });
});
