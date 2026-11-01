import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiIncidentPanel } from "@/components/fleet-ai-incident-panel";
describe("FleetAiIncidentPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiIncidentPanel incidents={50} open={2} resolved={48} mttr={15} aiAssisted={45} />);
    expect(container.textContent).toContain("Incident Response");
}); });
