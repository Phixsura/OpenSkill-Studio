import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAuditLogPanel } from "@/components/fleet-audit-log-panel";
describe("FleetAuditLogPanel", () => { it("renders", () => {
    const { container } = render(<FleetAuditLogPanel totalEvents={5000} types={12} />);
    expect(container.textContent).toContain("Audit Log");
    expect(container.textContent).toContain("5,000 events");
}); });
