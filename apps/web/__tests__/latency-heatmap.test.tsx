import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LatencyHeatmap } from "@/components/latency-heatmap";

describe("LatencyHeatmap", () => {
  it("renders heatmap", () => {
    const { container } = render(
      <LatencyHeatmap totalPairs={2} highestLatency="web→api" pairs={[
        { pair: "web→api", avgMs: 20, p99Ms: 45, samples: 100 },
        { pair: "api→db", avgMs: 6.5, p99Ms: 12, samples: 200 },
      ]} />
    );
    expect(container.textContent).toContain("Network Latency");
    expect(container.textContent).toContain("2 pairs");
    expect(container.textContent).toContain("web→api");
    expect(container.textContent).toContain("avg 20ms");
    expect(container.textContent).toContain("api→db");
  });
});
