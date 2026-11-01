import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNetworkSegmentationV9Panel } from "@/components/fleet-network-segmentation-v9-panel";
describe("FleetNetworkSegmentationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetNetworkSegmentationV9Panel segments={20} violations={0} />);
    expect(container.textContent).toContain("Network Segmentation v9");
}); });
