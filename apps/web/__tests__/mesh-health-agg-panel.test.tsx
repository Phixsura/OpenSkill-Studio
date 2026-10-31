import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshHealthAggPanel } from "@/components/mesh-health-agg-panel";
describe("MeshHealthAggPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MeshHealthAggPanel overall="healthy" total={5} healthy={5} degraded={0}
        down={0} avgLatencyMs={30} mtlsCoveragePct={100} healthPct={100} />
    );
    expect(container.textContent).toContain("Mesh: HEALTHY");
    expect(container.textContent).toContain("100% healthy");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("100%");
  });
});
