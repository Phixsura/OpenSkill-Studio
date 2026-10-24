import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiReadyGatePanel } from "@/components/fleet-ai-ready-gate-panel";
describe("FleetAiReadyGatePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiReadyGatePanel gates={4} active={4} services={200} ready={200} checks={20} />);
    expect(container.textContent).toContain("Readiness Gate");
}); });
