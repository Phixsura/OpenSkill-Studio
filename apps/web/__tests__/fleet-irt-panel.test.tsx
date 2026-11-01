import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIrtPanel } from "@/components/fleet-irt-panel";
describe("FleetIrtPanel", () => { it("renders", () => {
    const { container } = render(<FleetIrtPanel total={10} avgAck={12} withinSla={8} slaPct={80} />);
    expect(container.textContent).toContain("Incident Response");
    expect(container.textContent).toContain("80%");
}); });
