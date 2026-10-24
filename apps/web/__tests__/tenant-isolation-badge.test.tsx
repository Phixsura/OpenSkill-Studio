import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TenantIsolationBadge } from "@/components/tenant-isolation-badge";

describe("TenantIsolationBadge", () => {
  it("shows isolated", () => {
    const { container } = render(<TenantIsolationBadge orgId="org1" namespace="org_org1_app_a1" isolated={true} />);
    expect(container.textContent).toContain("Tenant Isolated");
    expect(container.textContent).toContain("org_org1_app_a1");
  });
  it("shows warning", () => {
    const { container } = render(<TenantIsolationBadge orgId="org1" namespace="shared" isolated={false} />);
    expect(container.textContent).toContain("Isolation Warning");
  });
});
