import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiMonitoringV9Panel } from "@/components/fleet-api-monitoring-v9-panel";
describe("FleetApiMonitoringV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiMonitoringV9Panel monitors={50} uptime={99.99} />);
    expect(container.textContent).toContain("API Monitoring v9");
}); });
