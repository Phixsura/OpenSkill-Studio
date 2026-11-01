import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TenantLimitPanel } from "@/components/tenant-limit-panel";
describe("TenantLimitPanel", () => {
  it("renders", () => {
    const { container } = render(
      <TenantLimitPanel tenantId="acme" exceeded={1} warnings={1}
        checks={[
          { resource: "api_calls", current: 50, limit: 100, pct: 50, exceeded: false, warning: false },
          { resource: "storage", current: 85, limit: 100, pct: 85, exceeded: false, warning: true },
          { resource: "bandwidth", current: 110, limit: 100, pct: 110, exceeded: true, warning: false },
        ]} />
    );
    expect(container.textContent).toContain("Tenant Limits: acme");
    expect(container.textContent).toContain("1 exceeded");
    expect(container.textContent).toContain("api_calls");
    expect(container.textContent).toContain("50/100");
    expect(container.textContent).toContain("bandwidth");
    expect(container.textContent).toContain("110/100");
  });
});
