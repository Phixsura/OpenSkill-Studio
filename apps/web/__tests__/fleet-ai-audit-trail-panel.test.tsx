import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAuditTrailPanel } from "@/components/fleet-ai-audit-trail-panel";
describe("FleetAiAuditTrailPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAuditTrailPanel trails={3} active={3} events={50000000} retention={730} tamperProof={true} />);
    expect(container.textContent).toContain("Audit Trail");
}); });
