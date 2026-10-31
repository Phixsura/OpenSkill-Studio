import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPostmortemPanel } from "@/components/fleet-postmortem-panel";
describe("FleetPostmortemPanel", () => { it("renders", () => {
    const { container } = render(<FleetPostmortemPanel total={10} postmortemsDone={8} actionsCompleted={6} completionPct={80} />);
    expect(container.textContent).toContain("Postmortems");
    expect(container.textContent).toContain("8/10 done");
}); });
