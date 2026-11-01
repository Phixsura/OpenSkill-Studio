import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiSecurityAuditV9Panel } from "@/components/fleet-api-security-audit-v9-panel";
describe("FleetApiSecurityAuditV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiSecurityAuditV9Panel audits={10} findings={5} />);
    expect(container.textContent).toContain("Security Audit v9");
}); });
