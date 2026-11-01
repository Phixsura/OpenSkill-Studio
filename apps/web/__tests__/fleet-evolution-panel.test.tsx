import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEvolutionPanel } from "@/components/fleet-evolution-panel";
describe("FleetEvolutionPanel", () => { it("renders", () => {
    const { container } = render(<FleetEvolutionPanel firstFiles={100} currentFiles={10000} growthPct={9900} accelerating={true} />);
    expect(container.textContent).toContain("Platform Evolution");
    expect(container.textContent).toContain("Rapid growth");
}); });
