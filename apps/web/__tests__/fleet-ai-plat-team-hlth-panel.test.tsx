import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatTeamHlthPanel } from "@/components/fleet-ai-plat-team-hlth-panel";
describe("FleetAiPlatTeamHlthPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatTeamHlthPanel trackers={3} active={3} teams={30} happiness={92} burnout={5} />);
    expect(container.textContent).toContain("Team Health");
}); });
