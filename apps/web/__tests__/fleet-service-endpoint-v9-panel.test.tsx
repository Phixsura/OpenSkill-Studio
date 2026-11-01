import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceEndpointV9Panel } from "@/components/fleet-service-endpoint-v9-panel";
describe("FleetServiceEndpointV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceEndpointV9Panel endpoints={100} ready={100} />);
    expect(container.textContent).toContain("Service Endpoint v9");
}); });
