import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TenantUsageMeter } from "@/components/tenant-usage-meter";

describe("TenantUsageMeter", () => {
  it("renders metering", () => {
    const { container } = render(
      <TenantUsageMeter topResource="api_calls"
        tenants={[{ tenantId: "t1", resources: {}, totalUnits: 500 }]}
        topTenants={[
          { tenantId: "t3", usage: 800 },
          { tenantId: "t1", usage: 500 },
        ]} />
    );
    expect(container.textContent).toContain("Tenant Metering");
    expect(container.textContent).toContain("1 tenants");
    expect(container.textContent).toContain("Top by api_calls");
    expect(container.textContent).toContain("t3");
    expect(container.textContent).toContain("800");
  });
});
