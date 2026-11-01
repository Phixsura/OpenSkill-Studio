import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIncidentPostmortemV9Panel } from "@/components/fleet-incident-postmortem-v9-panel";
describe("FleetIncidentPostmortemV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetIncidentPostmortemV9Panel total={20} resolved={18} />);
    expect(container.textContent).toContain("Postmortem v9");
}); });
