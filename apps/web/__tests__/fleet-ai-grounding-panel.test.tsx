import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGroundingPanel } from "@/components/fleet-ai-grounding-panel";
describe("FleetAiGroundingPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiGroundingPanel engines={3} active={3} responses={50000000} grounded={98} sources={200000000} />);
    expect(container.textContent).toContain("Grounding Engine");
}); });
