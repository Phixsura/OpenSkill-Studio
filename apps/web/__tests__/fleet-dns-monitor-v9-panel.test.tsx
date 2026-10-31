import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDnsMonitorV9Panel } from "@/components/fleet-dns-monitor-v9-panel";
describe("FleetDnsMonitorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDnsMonitorV9Panel domains={50} failures={0} />);
    expect(container.textContent).toContain("DNS Monitor v9");
}); });
