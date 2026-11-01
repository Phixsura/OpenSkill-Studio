import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTenantIsoPanel } from "@/components/fleet-tenant-iso-panel";
describe("FleetTenantIsoPanel", () => { it("renders", () => {
    const { container } = render(<FleetTenantIsoPanel total={10} isolated={8} shared={2} fullyIsolated={false} />);
    expect(container.textContent).toContain("Tenant Isolation");
    expect(container.textContent).toContain("2 shared");
}); });
