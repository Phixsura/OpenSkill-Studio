import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TenantOverview } from "@/components/tenant-overview";

describe("TenantOverview", () => {
  it("renders overview", () => {
    const { container } = render(
      <TenantOverview totalTenants={50} active={45} suspended={5}
        totalUsers={2500} totalStorageMb={50000} />
    );
    expect(container.textContent).toContain("Tenant Overview");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("45");
    expect(container.textContent).toContain("2500");
    expect(container.textContent).toContain("50000 MB");
  });
});
