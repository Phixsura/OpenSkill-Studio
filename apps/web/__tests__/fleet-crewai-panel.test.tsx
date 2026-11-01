import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCrewaiPanel } from "@/components/fleet-crewai-panel";
describe("FleetCrewaiPanel", () => { it("renders", () => {
    const { container } = render(<FleetCrewaiPanel crews={5} active={5} agents={30} tasks={25000} />);
    expect(container.textContent).toContain("CrewAI");
}); });
