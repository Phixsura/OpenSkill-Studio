import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LoadBalancerPanel } from "@/components/load-balancer-panel";

describe("LoadBalancerPanel", () => {
  it("renders LB", () => {
    const { container } = render(
      <LoadBalancerPanel status="degraded" totalRps={980} avgLatencyMs={47}
        healthyCount={2} unhealthyCount={1} backends={[
          { id: "i-1", healthy: true, rps: 500, latencyMs: 45 },
          { id: "i-2", healthy: true, rps: 480, latencyMs: 50 },
          { id: "i-3", healthy: false, rps: 0, latencyMs: 0 },
        ]} />
    );
    expect(container.textContent).toContain("Load Balancer");
    expect(container.textContent).toContain("degraded");
    expect(container.textContent).toContain("980");
    expect(container.textContent).toContain("i-1");
    expect(container.textContent).toContain("2/3");
  });
});
