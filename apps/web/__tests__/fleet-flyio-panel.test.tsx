import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFlyioPanel } from "@/components/fleet-flyio-panel";
describe("FleetFlyioPanel", () => { it("renders", () => {
    const { container } = render(<FleetFlyioPanel apps={10} running={10} machines={30} regions={5} />);
    expect(container.textContent).toContain("Fly.io");
    expect(container.textContent).toContain("5 regions");
}); });
