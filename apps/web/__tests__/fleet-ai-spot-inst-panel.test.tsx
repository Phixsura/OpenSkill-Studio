import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSpotInstPanel } from "@/components/fleet-ai-spot-inst-panel";
describe("FleetAiSpotInstPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSpotInstPanel managers={4} active={4} instances={500} savings={75} interruptions={8} />);
    expect(container.textContent).toContain("Spot Instances");
}); });
