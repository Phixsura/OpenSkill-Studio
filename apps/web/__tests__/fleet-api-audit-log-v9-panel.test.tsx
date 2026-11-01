import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiAuditLogV9Panel } from "@/components/fleet-api-audit-log-v9-panel";
describe("FleetApiAuditLogV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiAuditLogV9Panel sources={10} entries={100000} />);
    expect(container.textContent).toContain("API Audit Log v9");
}); });
