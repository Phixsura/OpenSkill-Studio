import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRbacAuditPanel } from "@/components/fleet-rbac-audit-panel";
describe("FleetRbacAuditPanel", () => { it("renders", () => {
    const { container } = render(<FleetRbacAuditPanel total={10} overprivileged={2} compliant={false} />);
    expect(container.textContent).toContain("RBAC Audit");
    expect(container.textContent).toContain("2 overprivileged");
}); });
