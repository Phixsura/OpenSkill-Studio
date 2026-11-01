import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFreshPanel } from "@/components/fleet-fresh-panel";
describe("FleetFreshPanel", () => { it("renders", () => {
    const { container } = render(<FleetFreshPanel apps={3} running={3} islands={30} routes={50} />);
    expect(container.textContent).toContain("Fresh");
    expect(container.textContent).toContain("30 islands");
}); });
