import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBicepPanel } from "@/components/fleet-bicep-panel";
describe("FleetBicepPanel", () => { it("renders", () => {
    const { container } = render(<FleetBicepPanel total={10} succeeded={9} failed={1} />);
    expect(container.textContent).toContain("Azure Bicep");
}); });
