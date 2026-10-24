import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetClusterUpgradeV9Panel } from "@/components/fleet-cluster-upgrade-v9-panel";
describe("FleetClusterUpgradeV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetClusterUpgradeV9Panel clusters={5} upgraded={5} />);
    expect(container.textContent).toContain("Cluster Upgrade v9");
}); });
