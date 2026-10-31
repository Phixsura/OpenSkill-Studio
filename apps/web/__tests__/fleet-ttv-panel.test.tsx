import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTtvPanel } from "@/components/fleet-ttv-panel";
describe("FleetTtvPanel", () => { it("renders", () => {
    const { container } = render(<FleetTtvPanel total={100} avgTtv={18} fastActivation={75} fastPct={75} />);
    expect(container.textContent).toContain("Time to Value");
    expect(container.textContent).toContain("75%");
}); });
