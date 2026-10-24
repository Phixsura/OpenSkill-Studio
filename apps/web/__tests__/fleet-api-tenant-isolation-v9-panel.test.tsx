import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiTenantIsolationV9Panel } from "@/components/fleet-api-tenant-isolation-v9-panel";
describe("FleetApiTenantIsolationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiTenantIsolationV9Panel tenants={100} violations={0} />);
    expect(container.textContent).toContain("Tenant Isolation v9");
}); });
