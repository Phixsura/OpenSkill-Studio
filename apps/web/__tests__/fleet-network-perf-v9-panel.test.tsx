import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNetworkPerfV9Panel } from "@/components/fleet-network-perf-v9-panel";
describe("FleetNetworkPerfV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetNetworkPerfV9Panel links={20} latency={5} />);
    expect(container.textContent).toContain("Network Perf v9");
}); });
