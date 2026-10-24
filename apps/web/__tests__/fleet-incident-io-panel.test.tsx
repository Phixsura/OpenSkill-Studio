import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIncidentIoPanel } from "@/components/fleet-incident-io-panel";
describe("FleetIncidentIoPanel", () => { it("renders", () => {
    const { container } = render(<FleetIncidentIoPanel total={20} active={2} resolved={18} avgTtd={5} avgTtr={30} />);
    expect(container.textContent).toContain("Incident.io");
    expect(container.textContent).toContain("TTR 30min");
}); });
