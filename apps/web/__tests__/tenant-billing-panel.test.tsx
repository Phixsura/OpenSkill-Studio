import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TenantBillingPanel } from "@/components/tenant-billing-panel";

describe("TenantBillingPanel", () => {
  it("renders", () => {
    const { container } = render(
      <TenantBillingPanel tenantId="acme-corp" total={17.5} currency="USD"
        lineItems={[
          { resource: "compute_hours", quantity: 150, rate: 0.1, cost: 15 },
          { resource: "storage_gb", quantity: 50, rate: 0.05, cost: 2.5 },
        ]} />
    );
    expect(container.textContent).toContain("Billing: acme-corp");
    expect(container.textContent).toContain("$17.5 USD");
    expect(container.textContent).toContain("compute_hours");
    expect(container.textContent).toContain("$15");
    expect(container.textContent).toContain("storage_gb");
  });
});
