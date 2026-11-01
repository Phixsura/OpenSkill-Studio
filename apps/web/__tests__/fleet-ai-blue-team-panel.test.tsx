import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiBlueTeamPanel } from "@/components/fleet-ai-blue-team-panel";
describe("FleetAiBlueTeamPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiBlueTeamPanel teams={4} active={4} incidents={200} detections={1000} responseMin={3} />);
    expect(container.textContent).toContain("Blue Teaming");
}); });
