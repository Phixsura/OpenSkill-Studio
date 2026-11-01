import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TenantUsageDashPanel } from "@/components/tenant-usage-dash-panel";
describe("TenantUsageDashPanel", () => {
  it("renders", () => {
    const { container } = render(
      <TenantUsageDashPanel tenantId="acme" plan="pro" status="warning"
        usage={{
          api_calls: { used: 85000, limit: 100000, pct: 85 },
          storage: { used: 20, limit: 100, pct: 20 },
        }} />
    );
    expect(container.textContent).toContain("Tenant: acme");
    expect(container.textContent).toContain("pro");
    expect(container.textContent).toContain("warning");
    expect(container.textContent).toContain("api calls");
    expect(container.textContent).toContain("85,000/100,000");
    expect(container.textContent).toContain("85%");
  });
});
