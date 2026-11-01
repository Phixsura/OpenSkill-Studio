import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshTimelinePanel } from "@/components/mesh-timeline-panel";
describe("MeshTimelinePanel", () => {
  it("renders", () => {
    const { container } = render(
      <MeshTimelinePanel trend="improving" currentPct={100} dataPoints={3}
        entries={[
          { healthPct: 80, status: "degraded" },
          { healthPct: 90, status: "degraded" },
          { healthPct: 100, status: "healthy" },
        ]} />
    );
    expect(container.textContent).toContain("Mesh Health Timeline");
    expect(container.textContent).toContain("improving");
    expect(container.textContent).toContain("100% healthy");
    expect(container.textContent).toContain("3 points");
  });
});
