import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatRoadmapPanel } from "@/components/fleet-ai-plat-roadmap-panel";
describe("FleetAiPlatRoadmapPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatRoadmapPanel roadmaps={2} active={2} planned={200} inProgress={50} completed={500} />);
    expect(container.textContent).toContain("Platform Roadmap");
}); });
