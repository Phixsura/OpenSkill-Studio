import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetReqPrioPanel } from "@/components/fleet-req-prio-panel";
describe("FleetReqPrioPanel", () => { it("renders", () => {
    const { container } = render(<FleetReqPrioPanel total={1000} highPriorityPct={20} />);
    expect(container.textContent).toContain("Request Priority");
    expect(container.textContent).toContain("20% high");
}); });
