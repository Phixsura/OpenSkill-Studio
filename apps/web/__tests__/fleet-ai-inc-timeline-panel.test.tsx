import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiIncTimelinePanel } from "@/components/fleet-ai-inc-timeline-panel";
describe("FleetAiIncTimelinePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiIncTimelinePanel trackers={3} active={3} incidents={500} events={20000} resolution={10} />);
    expect(container.textContent).toContain("Incident Timeline");
}); });
