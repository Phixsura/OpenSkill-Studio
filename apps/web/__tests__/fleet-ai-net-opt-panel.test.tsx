import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiNetOptPanel } from "@/components/fleet-ai-net-opt-panel";
describe("FleetAiNetOptPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiNetOptPanel optimizers={3} active={3} bandwidthSaved={55} latencyReduction={45} compression={6} />);
    expect(container.textContent).toContain("Network Optimizer");
}); });
