import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOverviewPanel } from "@/components/fleet-overview-panel";
describe("FleetOverviewPanel", () => {
  it("renders", () => {
    const { container } = render(
      <FleetOverviewPanel overall="healthy" total={10} healthPct={100} totalRps={16000}
        byStatus={{ healthy: 10 }} byTier={{ critical: 3, standard: 7 }} />
    );
    expect(container.textContent).toContain("Fleet: HEALTHY");
    expect(container.textContent).toContain("10 services");
    expect(container.textContent).toContain("100% healthy");
    expect(container.textContent).toContain("16,000 rps");
    expect(container.textContent).toContain("critical: 3");
    expect(container.textContent).toContain("standard: 7");
  });
});
