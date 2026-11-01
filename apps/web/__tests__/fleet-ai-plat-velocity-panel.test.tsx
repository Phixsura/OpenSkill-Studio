import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatVelocityPanel } from "@/components/fleet-ai-plat-velocity-panel";
describe("FleetAiPlatVelocityPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatVelocityPanel trackers={3} active={3} commits={1000} prs={200} cycleTime={4} />);
    expect(container.textContent).toContain("Platform Velocity");
}); });
