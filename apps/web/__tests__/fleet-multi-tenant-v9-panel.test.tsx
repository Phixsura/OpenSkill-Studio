import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMultiTenantV9Panel } from "@/components/fleet-multi-tenant-v9-panel";
describe("FleetMultiTenantV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetMultiTenantV9Panel tenants={100} noisy={0} />);
    expect(container.textContent).toContain("Multi-Tenant v9");
}); });
