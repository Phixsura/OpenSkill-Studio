import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiVelocityV7Panel } from "@/components/fleet-ai-velocity-v7-panel";
describe("FleetAiVelocityV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiVelocityV7Panel trackers={3} active={3} commits={2000} prs={400} cycle={2} features={100} />);
    expect(container.textContent).toContain("Velocity v7");
}); });
