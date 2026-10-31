import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSiemConnectorV9Panel } from "@/components/fleet-siem-connector-v9-panel";
describe("FleetSiemConnectorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSiemConnectorV9Panel connectors={5} events={500000} />);
    expect(container.textContent).toContain("SIEM Connector v9");
}); });
