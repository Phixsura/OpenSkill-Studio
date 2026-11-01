import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSlaPenaltyPanel } from "@/components/fleet-sla-penalty-panel";
describe("FleetSlaPenaltyPanel", () => { it("renders", () => {
    const { container } = render(<FleetSlaPenaltyPanel breaches={2} totalPenalty={6000} clean={false} />);
    expect(container.textContent).toContain("SLA Penalties");
    expect(container.textContent).toContain("$6,000");
}); });
