import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetConnDrainPanel } from "@/components/fleet-conn-drain-panel";
describe("FleetConnDrainPanel", () => { it("renders", () => {
    const { container } = render(<FleetConnDrainPanel total={20} draining={3} avgDrainSec={25} allDrained={false} />);
    expect(container.textContent).toContain("Connection Draining");
    expect(container.textContent).toContain("3 draining");
}); });
