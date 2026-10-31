import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAuditV5Panel } from "@/components/fleet-ai-audit-v5-panel";
describe("FleetAiAuditV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiAuditV5Panel auditors={3} active={3} events={2000000000} retention={1095} tamperProof={true} />);
    expect(container.textContent).toContain("Audit v5");
}); });
