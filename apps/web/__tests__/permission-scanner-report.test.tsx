import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PermissionScannerReport } from "@/components/permission-scanner-report";

describe("PermissionScannerReport", () => {
  const permissions = [
    { permission: "read_profile", label: "Read Profile", risk: "low", reason: "Basic info" },
    { permission: "access_billing", label: "Access Billing", risk: "critical", reason: "Payment" },
  ];
  it("renders", () => {
    const { container } = render(
      <PermissionScannerReport permissions={permissions} maxRisk="critical" safeToInstall={false} />
    );
    expect(container.textContent).toContain("Permissions");
    expect(container.textContent).toContain("Risk: critical");
    expect(container.textContent).toContain("Read Profile");
    expect(container.textContent).toContain("Access Billing");
  });
});
