import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetResLimitsPanel } from "@/components/fleet-res-limits-panel";
describe("FleetResLimitsPanel", () => { it("renders", () => {
    const { container } = render(<FleetResLimitsPanel total={20} noCpu={3} noMem={2} allLimited={false} />);
    expect(container.textContent).toContain("Resource Limits");
    expect(container.textContent).toContain("3 no CPU");
}); });
