import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetUptimeMonitorV9Panel } from "@/components/fleet-uptime-monitor-v9-panel";
describe("FleetUptimeMonitorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetUptimeMonitorV9Panel monitors={100} uptime={99.99} />);
    expect(container.textContent).toContain("Uptime Monitor v9");
}); });
