import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiInnovTrackPanel } from "@/components/fleet-ai-innov-track-panel";
describe("FleetAiInnovTrackPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiInnovTrackPanel trackers={3} active={3} experiments={1000} breakthroughs={50} papers={100} />);
    expect(container.textContent).toContain("Innovation Tracker");
}); });
