import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPdbPanel } from "@/components/fleet-pdb-panel";
describe("FleetPdbPanel", () => { it("renders", () => {
    const { container } = render(<FleetPdbPanel total={5} violated={1} allCompliant={false} />);
    expect(container.textContent).toContain("Fleet PDB");
    expect(container.textContent).toContain("1 PDB violations");
}); });
