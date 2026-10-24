import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetK8sUpgradeV9Panel } from "@/components/fleet-k8s-upgrade-v9-panel";
describe("FleetK8sUpgradeV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetK8sUpgradeV9Panel clusters={10} current={10} />);
    expect(container.textContent).toContain("K8s Upgrade v9");
}); });
