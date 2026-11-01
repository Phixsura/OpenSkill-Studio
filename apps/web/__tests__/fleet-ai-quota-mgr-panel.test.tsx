import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiQuotaMgrPanel } from "@/components/fleet-ai-quota-mgr-panel";
describe("FleetAiQuotaMgrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiQuotaMgrPanel quotas={5} active={5} tenants={1000} enforced={1000} throttled={30} />);
    expect(container.textContent).toContain("Quota Manager");
}); });
