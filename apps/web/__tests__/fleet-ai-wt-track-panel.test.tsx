import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiWtTrackPanel } from "@/components/fleet-ai-wt-track-panel";
describe("FleetAiWtTrackPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiWtTrackPanel trackers={4} active={4} models={200} checkpoints={10000} drift={8} />);
    expect(container.textContent).toContain("Weight Tracker");
}); });
