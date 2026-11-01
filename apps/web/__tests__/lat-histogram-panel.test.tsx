import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LatHistogramPanel } from "@/components/lat-histogram-panel";
describe("LatHistogramPanel", () => {
  it("renders", () => {
    const { container } = render(
      <LatHistogramPanel endpoint="/api/users" total={1000}
        buckets={{ le_50: 60, le_100: 80, le_500: 95, le_inf: 100 }} />
    );
    expect(container.textContent).toContain("Latency Histogram");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("1000 samples");
    expect(container.textContent).toContain("60%");
    expect(container.textContent).toContain("95%");
  });
});
