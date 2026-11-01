import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDepTrackPanel } from "@/components/fleet-ai-dep-track-panel";
describe("FleetAiDepTrackPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDepTrackPanel trackers={4} active={4} deps={1000} outdated={30} vulns={0} />);
    expect(container.textContent).toContain("Dependency Tracker");
}); });
