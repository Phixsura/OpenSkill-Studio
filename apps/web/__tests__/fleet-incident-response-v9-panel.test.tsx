import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIncidentResponseV9Panel } from "@/components/fleet-incident-response-v9-panel";
describe("FleetIncidentResponseV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetIncidentResponseV9Panel teams={10} onCall={10} />);
    expect(container.textContent).toContain("Incident Response v9");
}); });
