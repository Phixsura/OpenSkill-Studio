import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiDiscoveryV9Panel } from "@/components/fleet-api-discovery-v9-panel";
describe("FleetApiDiscoveryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiDiscoveryV9Panel sources={10} discovered={200} />);
    expect(container.textContent).toContain("API Discovery v9");
}); });
