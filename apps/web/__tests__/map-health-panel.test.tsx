import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MapHealthPanel } from "@/components/map-health-panel";
describe("MapHealthPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MapHealthPanel healthyNodes={1} totalNodes={2}
        nodes={[{ name: "api", health: "healthy" }, { name: "db", health: "degraded" }]}
        edges={[{ source: "api", destination: "db", edgeHealth: "degraded", latencyMs: 5 }]} />
    );
    expect(container.textContent).toContain("Service Map Health");
    expect(container.textContent).toContain("1/2 healthy");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("api → db");
    expect(container.textContent).toContain("degraded");
  });
});
