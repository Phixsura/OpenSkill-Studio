import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGoldenPathPanel } from "@/components/fleet-golden-path-panel";
describe("FleetGoldenPathPanel", () => { it("renders", () => {
    const { container } = render(<FleetGoldenPathPanel total={20} onGoldenPath={15} offPath={5} adoptionPct={75} />);
    expect(container.textContent).toContain("Golden Path");
    expect(container.textContent).toContain("5 off golden path");
}); });
