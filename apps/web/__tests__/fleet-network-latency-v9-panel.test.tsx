import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNetworkLatencyV9Panel } from "@/components/fleet-network-latency-v9-panel";
describe("FleetNetworkLatencyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetNetworkLatencyV9Panel paths={100} avg={5} />);
    expect(container.textContent).toContain("Network Latency v9");
}); });
