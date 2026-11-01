import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEdgedbPanel } from "@/components/fleet-edgedb-panel";
describe("FleetEdgedbPanel", () => { it("renders", () => {
    const { container } = render(<FleetEdgedbPanel instances={3} available={3} branches={10} types={150} />);
    expect(container.textContent).toContain("EdgeDB");
    expect(container.textContent).toContain("150 types");
}); });
