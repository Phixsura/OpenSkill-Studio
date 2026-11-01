import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshSummaryPanel } from "@/components/mesh-summary-panel";
describe("MeshSummaryPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MeshSummaryPanel overall="healthy" totalServices={5} healthy={5}
        totalRps={5000} errorRatePct={0.1} mtlsPct={100} avgLatencyMs={45} />
    );
    expect(container.textContent).toContain("Service Mesh: HEALTHY");
    expect(container.textContent).toContain("5/5 healthy");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("0.1%");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("45ms");
  });
});
