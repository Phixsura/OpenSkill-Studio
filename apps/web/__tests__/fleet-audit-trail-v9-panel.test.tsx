import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAuditTrailV9Panel } from "@/components/fleet-audit-trail-v9-panel";
describe("FleetAuditTrailV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetAuditTrailV9Panel events={100000} critical={5} />);
    expect(container.textContent).toContain("Audit Trail v9");
}); });
