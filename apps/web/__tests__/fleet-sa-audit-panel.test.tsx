import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSaAuditPanel } from "@/components/fleet-sa-audit-panel";
describe("FleetSaAuditPanel", () => { it("renders", () => {
    const { container } = render(<FleetSaAuditPanel total={15} unused={3} withLongTokens={2} clean={false} />);
    expect(container.textContent).toContain("SA Audit");
    expect(container.textContent).toContain("3 unused");
}); });
