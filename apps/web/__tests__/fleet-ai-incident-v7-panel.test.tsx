import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiIncidentV7Panel } from "@/components/fleet-ai-incident-v7-panel";
describe("FleetAiIncidentV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiIncidentV7Panel managers={3} active={3} incidents={20} p1={3} mttr={3} postmortems={3} />);
    expect(container.textContent).toContain("Incident v7");
}); });
