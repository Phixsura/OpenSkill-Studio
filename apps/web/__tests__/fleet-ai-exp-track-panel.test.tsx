import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiExpTrackPanel } from "@/components/fleet-ai-exp-track-panel";
describe("FleetAiExpTrackPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiExpTrackPanel trackers={4} active={4} experiments={200} runs={10000} bestMetric={99.1} />);
    expect(container.textContent).toContain("Experiment Tracker");
}); });
