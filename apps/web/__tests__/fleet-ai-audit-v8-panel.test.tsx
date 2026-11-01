import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAuditV8Panel } from "@/components/fleet-ai-audit-v8-panel";
describe("FleetAiAuditV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiAuditV8Panel auditors={3} active={3} events={5000000000} retention={3650} tamperProof={true} />);
    expect(container.textContent).toContain("Audit v8");
}); });
