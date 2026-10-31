import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiLossTrackPanel } from "@/components/fleet-ai-loss-track-panel";
describe("FleetAiLossTrackPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiLossTrackPanel trackers={3} active={3} jobs={100} loss={0.3} converged={80} />);
    expect(container.textContent).toContain("Loss Tracker");
}); });
