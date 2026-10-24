import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTursoEdgePanel } from "@/components/fleet-turso-edge-panel";
describe("FleetTursoEdgePanel", () => { it("renders", () => {
    const { container } = render(<FleetTursoEdgePanel groups={3} primary={3} replicas={15} locations={8} />);
    expect(container.textContent).toContain("Turso Edge");
}); });
