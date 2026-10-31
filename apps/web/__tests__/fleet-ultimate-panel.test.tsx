import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetUltimatePanel } from "@/components/fleet-ultimate-panel";
describe("FleetUltimatePanel", () => { it("renders", () => {
    const { container } = render(<FleetUltimatePanel />);
    expect(container.textContent).toContain("ALL SYSTEMS GO");
    expect(container.textContent).toContain("FULLY OPERATIONAL");
}); });
