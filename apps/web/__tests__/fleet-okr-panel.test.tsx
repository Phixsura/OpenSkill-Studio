import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOkrPanel } from "@/components/fleet-okr-panel";
describe("FleetOkrPanel", () => { it("renders", () => {
    const { container } = render(<FleetOkrPanel total={10} onTrack={6} atRisk={3} behind={1} avgProgress={65} />);
    expect(container.textContent).toContain("OKRs");
    expect(container.textContent).toContain("65%");
}); });
