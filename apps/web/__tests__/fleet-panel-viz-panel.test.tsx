import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPanelVizPanel } from "@/components/fleet-panel-viz-panel";
describe("FleetPanelVizPanel", () => { it("renders", () => {
    const { container } = render(<FleetPanelVizPanel apps={5} running={5} widgets={200} sessions={20000} />);
    expect(container.textContent).toContain("Panel");
}); });
