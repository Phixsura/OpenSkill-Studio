import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TrafficAnalyzePanel } from "@/components/traffic-analyze-panel";
describe("TrafficAnalyzePanel", () => {
  it("renders", () => {
    const { container } = render(
      <TrafficAnalyzePanel total={10000} avgLatencyMs={45} errorRatePct={0.5}
        spikeDetected={false} byMethod={{ GET: 7000, POST: 3000 }}
        topEndpoints={[{ endpoint: "/users", count: 5000 }, { endpoint: "/orders", count: 3000 }]} />
    );
    expect(container.textContent).toContain("Traffic Analysis");
    expect(container.textContent).toContain("10,000 reqs");
    expect(container.textContent).toContain("45ms avg");
    expect(container.textContent).toContain("GET: 7000");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("5,000");
  });
});
