import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetContainerRegistryV9Panel } from "@/components/fleet-container-registry-v9-panel";
describe("FleetContainerRegistryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetContainerRegistryV9Panel images={500} vulns={0} />);
    expect(container.textContent).toContain("Container Registry v9");
}); });
