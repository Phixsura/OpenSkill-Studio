import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRoadmapV7Panel } from "@/components/fleet-ai-roadmap-v7-panel";
describe("FleetAiRoadmapV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiRoadmapV7Panel roadmaps={3} active={3} planned={300} inProgress={80} shipped={1000} onTime={95} />);
    expect(container.textContent).toContain("Roadmap v7");
}); });
