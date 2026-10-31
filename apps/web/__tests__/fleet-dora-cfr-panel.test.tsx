import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDoraCfrPanel } from "@/components/fleet-dora-cfr-panel";
describe("FleetDoraCfrPanel", () => { it("renders", () => {
    const { container } = render(<FleetDoraCfrPanel cfrPct={3} level="Elite" />);
    expect(container.textContent).toContain("DORA: CFR");
    expect(container.textContent).toContain("Elite");
}); });
