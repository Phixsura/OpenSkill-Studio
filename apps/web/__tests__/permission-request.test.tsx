import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PermissionRequest } from "@/components/permission-request";

describe("PermissionRequest", () => {
  const permissions = [
    { id: "read:profile", label: "Read Profile", description: "Access name", risk: "low", icon: "👤" },
    { id: "admin:org", label: "Org Admin", description: "Full access", risk: "high", icon: "🏢" },
  ];
  it("renders permission request", () => {
    const { container } = render(
      <PermissionRequest permissions={permissions} maxRisk="high" requiresAdmin={true}
        appName="SuperApp" onAllow={vi.fn()} onDeny={vi.fn()} />
    );
    expect(container.textContent).toContain("SuperApp requests access");
    expect(container.textContent).toContain("Read Profile");
    expect(container.textContent).toContain("Org Admin");
    expect(container.textContent).toContain("admin approval");
    expect(container.textContent).toContain("Allow");
    expect(container.textContent).toContain("Deny");
  });
});
