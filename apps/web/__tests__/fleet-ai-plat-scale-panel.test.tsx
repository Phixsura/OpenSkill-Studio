import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatScalePanel } from "@/components/fleet-ai-plat-scale-panel";
describe("FleetAiPlatScalePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatScalePanel trackers={4} active={4} maxRps={50000000} currentRps={25000000} headroom={50} autoScale={true} />);
    expect(container.textContent).toContain("AI Scalability");
}); });
