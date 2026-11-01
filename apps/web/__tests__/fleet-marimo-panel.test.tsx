import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMarimoPanel } from "@/components/fleet-marimo-panel";
describe("FleetMarimoPanel", () => { it("renders", () => {
    const { container } = render(<FleetMarimoPanel notebooks={10} running={10} cells={500} users={20000} />);
    expect(container.textContent).toContain("Marimo");
}); });
