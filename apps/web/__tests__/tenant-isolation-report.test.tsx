import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TenantIsolationReport } from "@/components/tenant-isolation-report";

describe("TenantIsolationReport", () => {
  it("renders secure", () => {
    const { container } = render(
      <TenantIsolationReport status="secure" summary="10 resources across 3 tenants"
        verdict="✅ All data properly isolated" violations={[]} />
    );
    expect(container.textContent).toContain("Tenant Isolation");
    expect(container.textContent).toContain("secure");
    expect(container.textContent).toContain("properly isolated");
  });

  it("renders violation", () => {
    const { container } = render(
      <TenantIsolationReport status="breached" summary="5 resources"
        verdict="❌ 1 violation" violations={[
          { resource: "r1", owner: "t1", accessedBy: "t2", severity: "high" },
        ]} />
    );
    expect(container.textContent).toContain("breached");
    expect(container.textContent).toContain("accessed by t2");
  });
});
