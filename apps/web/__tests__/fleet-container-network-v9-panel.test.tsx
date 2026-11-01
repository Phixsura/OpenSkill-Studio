import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetContainerNetworkV9Panel } from "@/components/fleet-container-network-v9-panel";
describe("FleetContainerNetworkV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetContainerNetworkV9Panel plugins={3} pods={500} />);
    expect(container.textContent).toContain("Container Network v9");
}); });
