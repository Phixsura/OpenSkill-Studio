import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNetworkPanel } from "@/components/fleet-network-panel";
describe("FleetNetworkPanel", () => { it("renders", () => {
    const { container } = render(<FleetNetworkPanel rxMbps={300} txMbps={200} totalMbps={500} />);
    expect(container.textContent).toContain("Fleet Network");
    expect(container.textContent).toContain("Total 500 Mbps");
}); });
