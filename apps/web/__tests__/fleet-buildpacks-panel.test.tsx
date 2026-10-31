import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBuildpacksPanel } from "@/components/fleet-buildpacks-panel";
describe("FleetBuildpacksPanel", () => { it("renders", () => {
    const { container } = render(<FleetBuildpacksPanel total={20} usingBp={12} usingDockerfile={8} avgBuild={90} />);
    expect(container.textContent).toContain("Buildpacks");
    expect(container.textContent).toContain("12 buildpacks");
}); });
