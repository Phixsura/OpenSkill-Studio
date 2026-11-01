import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetChefPanel } from "@/components/fleet-chef-panel";
describe("FleetChefPanel", () => { it("renders", () => {
    const { container } = render(<FleetChefPanel profiles={10} passed={90} failed={5} skipped={5} compliancePct={90} />);
    expect(container.textContent).toContain("Chef InSpec");
    expect(container.textContent).toContain("90% compliant");
}); });
