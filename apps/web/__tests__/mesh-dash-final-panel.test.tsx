import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshDashFinalPanel } from "@/components/mesh-dash-final-panel";
describe("MeshDashFinalPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MeshDashFinalPanel score={100} status="healthy" healthy={10} total={10}
        rps={5000} errorRatePct={0.1} p99Ms={100} mtlsPct={100}
        circuitTrips={0} retries={50} />
    );
    expect(container.textContent).toContain("100/100");
    expect(container.textContent).toContain("Mesh: HEALTHY");
    expect(container.textContent).toContain("10/10 healthy");
    expect(container.textContent).toContain("5,000 rps");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("0.1%");
  });
});
