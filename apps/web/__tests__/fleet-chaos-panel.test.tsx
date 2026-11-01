import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetChaosPanel } from "@/components/fleet-chaos-panel";
describe("FleetChaosPanel", () => { it("renders", () => {
    const { container } = render(<FleetChaosPanel total={5} passed={3} weaknessesFound={2} resilient={false} />);
    expect(container.textContent).toContain("Chaos Engineering");
    expect(container.textContent).toContain("Issues found");
}); });
