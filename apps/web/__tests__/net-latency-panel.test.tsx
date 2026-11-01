import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NetLatencyPanel } from "@/components/net-latency-panel";
describe("NetLatencyPanel", () => {
  it("renders", () => {
    const { container } = render(
      <NetLatencyPanel totalMeasurements={1000}
        pairs={[
          { source: "api", destination: "db", avgMs: 5, p99Ms: 15, samples: 500 },
          { source: "web", destination: "api", avgMs: 20, p99Ms: 80, samples: 500 },
        ]} />
    );
    expect(container.textContent).toContain("Network Latency");
    expect(container.textContent).toContain("2 pairs");
    expect(container.textContent).toContain("1,000 measurements");
    expect(container.textContent).toContain("api → db");
    expect(container.textContent).toContain("avg 5ms");
    expect(container.textContent).toContain("p99 15ms");
  });
});
