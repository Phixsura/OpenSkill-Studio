import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTeamMgrPanel } from "@/components/fleet-ai-team-mgr-panel";
describe("FleetAiTeamMgrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTeamMgrPanel managers={2} active={2} teams={100} members={1000} projects={500} />);
    expect(container.textContent).toContain("Team Manager");
}); });
