import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCircuitResPanel } from "@/components/fleet-circuit-res-panel";
describe("FleetCircuitResPanel", () => { it("renders", () => {
    const { container } = render(<FleetCircuitResPanel total={10} closed={10} trips={3} avgRecovery={45} resilient={true} />);
    expect(container.textContent).toContain("Circuit Resilience");
    expect(container.textContent).toContain("Resilient");
}); });
