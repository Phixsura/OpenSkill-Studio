import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDbConnectionMonitorV9Panel } from "@/components/fleet-db-connection-monitor-v9-panel";
describe("FleetDbConnectionMonitorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDbConnectionMonitorV9Panel pools={5} utilization={30} />);
    expect(container.textContent).toContain("DB Connection Monitor v9");
}); });
