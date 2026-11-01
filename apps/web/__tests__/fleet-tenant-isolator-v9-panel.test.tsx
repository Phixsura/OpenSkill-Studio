import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTenantIsolatorV9Panel } from "@/components/fleet-tenant-isolator-v9-panel";
describe("FleetTenantIsolatorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetTenantIsolatorV9Panel tenants={50} violations={0} />);
    expect(container.textContent).toContain("Tenant Isolator v9");
}); });
