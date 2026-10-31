import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSlsaPanel } from "@/components/fleet-slsa-panel";
describe("FleetSlsaPanel", () => { it("renders", () => {
    const { container } = render(<FleetSlsaPanel total={50} avgLevel={2.5} mature={true} />);
    expect(container.textContent).toContain("SLSA");
    expect(container.textContent).toContain("Level 2.5");
}); });
