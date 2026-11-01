import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWaspPanel } from "@/components/fleet-wasp-panel";
describe("FleetWaspPanel", () => { it("renders", () => {
    const { container } = render(<FleetWaspPanel apps={5} deployed={5} entities={50} operations={120} />);
    expect(container.textContent).toContain("Wasp");
    expect(container.textContent).toContain("120 ops");
}); });
