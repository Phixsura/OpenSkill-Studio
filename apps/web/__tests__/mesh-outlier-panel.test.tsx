import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshOutlierPanel } from "@/components/mesh-outlier-panel";
describe("MeshOutlierPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MeshOutlierPanel total={5} meanError={3.11} ejectionsNeeded={1}
        outliers={[{ instance: "i5", errorRate: 15, zScore: 2.5 }]} />
    );
    expect(container.textContent).toContain("Mesh Outliers");
    expect(container.textContent).toContain("1 outliers");
    expect(container.textContent).toContain("5 instances");
    expect(container.textContent).toContain("i5");
    expect(container.textContent).toContain("15% err");
    expect(container.textContent).toContain("EJECT");
  });
});
