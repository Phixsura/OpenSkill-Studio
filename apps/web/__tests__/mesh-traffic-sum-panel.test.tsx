import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshTrafficSumPanel } from "@/components/mesh-traffic-sum-panel";
describe("MeshTrafficSumPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MeshTrafficSumPanel totalRps={2300} totalRequests={138000} errorRatePct={0.05}
        uniqueFlows={3} byProtocol={{ "HTTP/2": 108000, "gRPC": 30000 }}
        topFlows={[
          { source: "web", destination: "api", rps: 1000 },
          { source: "api", destination: "cache", rps: 800 },
        ]} />
    );
    expect(container.textContent).toContain("Mesh Traffic Summary");
    expect(container.textContent).toContain("2,300 rps");
    expect(container.textContent).toContain("3 flows");
    expect(container.textContent).toContain("HTTP/2: 108,000");
    expect(container.textContent).toContain("web → api");
    expect(container.textContent).toContain("1,000 rps");
  });
});
