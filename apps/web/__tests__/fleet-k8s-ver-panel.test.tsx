import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetK8sVerPanel } from "@/components/fleet-k8s-ver-panel";
describe("FleetK8sVerPanel", () => { it("renders", () => {
    const { container } = render(<FleetK8sVerPanel total={10} versionCount={2} skewed={true} />);
    expect(container.textContent).toContain("K8s Versions");
    expect(container.textContent).toContain("Version skew");
}); });
