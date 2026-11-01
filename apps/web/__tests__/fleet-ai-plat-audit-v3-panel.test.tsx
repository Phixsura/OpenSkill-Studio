import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatAuditV3Panel } from "@/components/fleet-ai-plat-audit-v3-panel";
describe("FleetAiPlatAuditV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatAuditV3Panel auditors={3} active={3} events={500000000} retention={1095} reports={1000} />);
    expect(container.textContent).toContain("Platform Audit v3");
}); });
