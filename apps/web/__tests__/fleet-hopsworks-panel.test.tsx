import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHopsworksPanel } from "@/components/fleet-hopsworks-panel";
describe("FleetHopsworksPanel", () => { it("renders", () => {
    const { container } = render(<FleetHopsworksPanel clusters={3} running={3} featureGroups={200} models={100} />);
    expect(container.textContent).toContain("Hopsworks");
}); });
