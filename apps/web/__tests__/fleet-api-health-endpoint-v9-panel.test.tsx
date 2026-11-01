import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiHealthEndpointV9Panel } from "@/components/fleet-api-health-endpoint-v9-panel";
describe("FleetApiHealthEndpointV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiHealthEndpointV9Panel services={200} health={200} />);
    expect(container.textContent).toContain("Health Endpoint v9");
}); });
