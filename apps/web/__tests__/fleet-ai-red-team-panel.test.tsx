import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRedTeamPanel } from "@/components/fleet-ai-red-team-panel";
describe("FleetAiRedTeamPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRedTeamPanel teams={3} active={3} attacks={50000} vulns={30} fixed={30} />);
    expect(container.textContent).toContain("Red Teaming");
}); });
