import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNetworkMonitorV9Panel } from "@/components/fleet-network-monitor-v9-panel";
describe("FleetNetworkMonitorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetNetworkMonitorV9Panel interfaces={50} errors={0} />);
    expect(container.textContent).toContain("Network Monitor v9");
}); });
