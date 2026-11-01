import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRelCadencePanel } from "@/components/fleet-rel-cadence-panel";
describe("FleetRelCadencePanel", () => { it("renders", () => {
    const { container } = render(<FleetRelCadencePanel total={12} avgGapDays={7} regular={true} />);
    expect(container.textContent).toContain("Release Cadence");
    expect(container.textContent).toContain("Regular");
}); });
