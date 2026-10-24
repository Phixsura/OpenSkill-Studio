import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTursoPanel } from "@/components/fleet-turso-panel";
describe("FleetTursoPanel", () => { it("renders", () => {
    const { container } = render(<FleetTursoPanel databases={10} replicas={30} totalRows={5000000} locations={5} />);
    expect(container.textContent).toContain("Turso");
    expect(container.textContent).toContain("5 locations");
}); });
