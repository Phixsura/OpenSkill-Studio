import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiLatTrackPanel } from "@/components/fleet-ai-lat-track-panel";
describe("FleetAiLatTrackPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiLatTrackPanel trackers={5} active={5} endpoints={1000} p50={20} p99={80} />);
    expect(container.textContent).toContain("Latency Tracker");
}); });
