import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetContainerProbeV9Panel } from "@/components/fleet-container-probe-v9-panel";
describe("FleetContainerProbeV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetContainerProbeV9Panel containers={500} liveness={500} />);
    expect(container.textContent).toContain("Container Probe v9");
}); });
