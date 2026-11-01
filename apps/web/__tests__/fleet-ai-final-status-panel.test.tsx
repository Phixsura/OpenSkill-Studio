import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiFinalStatusPanel } from "@/components/fleet-ai-final-status-panel";
describe("FleetAiFinalStatusPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiFinalStatusPanel total={1000} operational={1000} degraded={0} down={0} uptime={99.999} status="🟢 ALL OPERATIONAL" />);
    expect(container.textContent).toContain("Final Status");
}); });
