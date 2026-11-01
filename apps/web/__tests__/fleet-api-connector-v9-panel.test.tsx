import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiConnectorV9Panel } from "@/components/fleet-api-connector-v9-panel";
describe("FleetApiConnectorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiConnectorV9Panel connectors={30} connected={30} />);
    expect(container.textContent).toContain("API Connector v9");
}); });
