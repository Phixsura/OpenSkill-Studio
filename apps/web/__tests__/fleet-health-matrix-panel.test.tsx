import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHealthMatrixPanel } from "@/components/fleet-health-matrix-panel";
describe("FleetHealthMatrixPanel", () => { it("renders", () => {
    const { container } = render(<FleetHealthMatrixPanel dimensions={4} avgScore={84} weakest="cost" strongest="reliability" balanced={false} />);
    expect(container.textContent).toContain("Health Matrix");
    expect(container.textContent).toContain("Imbalanced");
}); });
