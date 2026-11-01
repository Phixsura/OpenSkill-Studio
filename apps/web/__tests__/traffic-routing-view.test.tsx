import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TrafficRoutingView } from "@/components/traffic-routing-view";

describe("TrafficRoutingView", () => {
  it("renders routes", () => {
    const { container } = render(
      <TrafficRoutingView routeCount={2} routes={[
        { path: "/api", targets: [{ backend: "v1", weight: 90 }, { backend: "v2", weight: 10 }] },
        { path: "/web", targets: [{ backend: "main", weight: 100 }] },
      ]} />
    );
    expect(container.textContent).toContain("Traffic Routing");
    expect(container.textContent).toContain("2 routes");
    expect(container.textContent).toContain("/api");
    expect(container.textContent).toContain("v1");
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("/web");
  });
});
