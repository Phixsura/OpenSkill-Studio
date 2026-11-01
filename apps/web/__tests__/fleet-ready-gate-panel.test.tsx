import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetReadyGatePanel } from "@/components/fleet-ready-gate-panel";
describe("FleetReadyGatePanel", () => { it("renders", () => {
    const { container } = render(<FleetReadyGatePanel total={5} passed={4} blocked={1} allClear={false} />);
    expect(container.textContent).toContain("Readiness Gates");
    expect(container.textContent).toContain("1 blocked");
}); });
