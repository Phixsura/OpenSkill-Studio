import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqFlowVizPanel } from "@/components/req-flow-viz-panel";
describe("ReqFlowVizPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReqFlowVizPanel totalMs={75} bottleneck="api"
        nodes={[
          { id: "s0", label: "gateway", operation: "route", durationMs: 5 },
          { id: "s1", label: "api", operation: "handle", durationMs: 50 },
          { id: "s2", label: "db", operation: "query", durationMs: 20 },
        ]} />
    );
    expect(container.textContent).toContain("Request Flow");
    expect(container.textContent).toContain("75ms total");
    expect(container.textContent).toContain("bottleneck: api");
    expect(container.textContent).toContain("gateway");
    expect(container.textContent).toContain("route");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("query");
  });
});
