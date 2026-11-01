import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceDiscoveryV9Panel } from "@/components/fleet-service-discovery-v9-panel";
describe("FleetServiceDiscoveryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceDiscoveryV9Panel services={100} endpoints={300} />);
    expect(container.textContent).toContain("Service Discovery v9");
}); });
