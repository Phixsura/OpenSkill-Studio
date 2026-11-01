import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CardinalityAnalyzer } from "@/components/cardinality-analyzer";

describe("CardinalityAnalyzer", () => {
  it("renders", () => {
    const { container } = render(
      <CardinalityAnalyzer totalMetrics={10} totalSeries={50100} highCardCount={1} costFactor={5}
        highCardinality={[
          { metric: "http_requests", series: 50000, labels: 5, recommendation: "Reduce label cardinality" },
        ]} />
    );
    expect(container.textContent).toContain("Metric Cardinality");
    expect(container.textContent).toContain("50,100 series");
    expect(container.textContent).toContain("1 high-cardinality");
    expect(container.textContent).toContain("http_requests");
    expect(container.textContent).toContain("Reduce label cardinality");
  });
});
