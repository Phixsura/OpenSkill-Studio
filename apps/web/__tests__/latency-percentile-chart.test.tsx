import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LatencyPercentileChart } from "@/components/latency-percentile-chart";

describe("LatencyPercentileChart", () => {
  it("renders chart", () => {
    const { container } = render(
      <LatencyPercentileChart p50={50} p90={120} p95={180} p99={300}
        avg={75} max={500} count={10000} sloMet={false} />
    );
    expect(container.textContent).toContain("Latency Percentiles");
    expect(container.textContent).toContain("10000 samples");
    expect(container.textContent).toContain("avg 75ms");
    expect(container.textContent).toContain("p50");
    expect(container.textContent).toContain("50ms");
    expect(container.textContent).toContain("p99");
    expect(container.textContent).toContain("300ms");
    expect(container.textContent).toContain("SLO breach");
  });
});
