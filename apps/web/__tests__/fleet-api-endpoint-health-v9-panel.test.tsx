import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiEndpointHealthV9Panel } from "@/components/fleet-api-endpoint-health-v9-panel";
describe("FleetApiEndpointHealthV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiEndpointHealthV9Panel endpoints={200} score={98} />);
    expect(container.textContent).toContain("Endpoint Health v9");
}); });
