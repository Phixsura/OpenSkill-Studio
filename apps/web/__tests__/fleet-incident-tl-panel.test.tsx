import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIncidentTlPanel } from "@/components/fleet-incident-tl-panel";
describe("FleetIncidentTlPanel", () => { it("renders", () => {
    const { container } = render(<FleetIncidentTlPanel total={5} sev1={1} sev2={2} resolved={3} open={2} />);
    expect(container.textContent).toContain("Incident Timeline");
    expect(container.textContent).toContain("2 open");
}); });
