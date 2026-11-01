import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatCapV3Panel } from "@/components/fleet-ai-plat-cap-v3-panel";
describe("FleetAiPlatCapV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatCapV3Panel planners={4} active={4} forecasts={1000} accuracy={97} headroom={40} />);
    expect(container.textContent).toContain("AI Capacity v3");
}); });
