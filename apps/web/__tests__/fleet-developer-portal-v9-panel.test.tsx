import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDeveloperPortalV9Panel } from "@/components/fleet-developer-portal-v9-panel";
describe("FleetDeveloperPortalV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDeveloperPortalV9Panel portals={3} devs={500} />);
    expect(container.textContent).toContain("Developer Portal v9");
}); });
