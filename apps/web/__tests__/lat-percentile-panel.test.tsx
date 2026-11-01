import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LatPercentilePanel } from "@/components/lat-percentile-panel";
describe("LatPercentilePanel", () => {
  it("renders", () => {
    const { container } = render(
      <LatPercentilePanel samples={10000} p50={45} p90={120} p95={200} p99={500} avg={65} />
    );
    expect(container.textContent).toContain("Latency Percentiles");
    expect(container.textContent).toContain("10,000 samples");
    expect(container.textContent).toContain("avg 65ms");
    expect(container.textContent).toContain("45ms");
    expect(container.textContent).toContain("120ms");
    expect(container.textContent).toContain("200ms");
    expect(container.textContent).toContain("500ms");
  });
});
