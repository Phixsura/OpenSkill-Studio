import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetClusterMonitoringV9Panel } from "@/components/fleet-cluster-monitoring-v9-panel";
describe("FleetClusterMonitoringV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetClusterMonitoringV9Panel clusters={5} alerts={0} />);
    expect(container.textContent).toContain("Cluster Monitoring v9");
}); });
