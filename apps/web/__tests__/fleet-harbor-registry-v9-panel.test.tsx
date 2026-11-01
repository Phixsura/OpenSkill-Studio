import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHarborRegistryV9Panel } from "@/components/fleet-harbor-registry-v9-panel";
describe("FleetHarborRegistryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetHarborRegistryV9Panel registries={3} images={500} />);
    expect(container.textContent).toContain("Harbor Registry v9");
}); });
