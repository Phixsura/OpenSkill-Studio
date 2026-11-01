import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatRoiPanel } from "@/components/fleet-ai-plat-roi-panel";
describe("FleetAiPlatRoiPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatRoiPanel trackers={2} active={2} investment={5000000} returns={25000000} roi={400} />);
    expect(container.textContent).toContain("Platform ROI");
}); });
