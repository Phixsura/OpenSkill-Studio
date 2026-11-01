import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TenantIsolateReport } from "@/components/tenant-isolate-report";

describe("TenantIsolateReport", () => {
  it("renders violations", () => {
    const { container } = render(
      <TenantIsolateReport valid={false} tenantsChecked={3} resourcesChecked={10}
        violations={[
          { resourceId: "shared-db", tenants: ["t1", "t2"], severity: "critical" },
        ]} />
    );
    expect(container.textContent).toContain("Tenant Isolation");
    expect(container.textContent).toContain("1 violations");
    expect(container.textContent).toContain("3 tenants");
    expect(container.textContent).toContain("shared-db");
    expect(container.textContent).toContain("t1, t2");
  });
});
