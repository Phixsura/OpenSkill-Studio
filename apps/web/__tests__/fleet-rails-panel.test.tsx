import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRailsPanel } from "@/components/fleet-rails-panel";
describe("FleetRailsPanel", () => { it("renders", () => {
    const { container } = render(<FleetRailsPanel apps={10} running={10} rps={50000} dbPoolPct={55} />);
    expect(container.textContent).toContain("Rails");
    expect(container.textContent).toContain("50,000");
}); });
