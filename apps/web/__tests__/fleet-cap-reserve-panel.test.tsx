import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCapReservePanel } from "@/components/fleet-cap-reserve-panel";
describe("FleetCapReservePanel", () => { it("renders", () => {
    const { container } = render(<FleetCapReservePanel reserved={200} used={50} utilPct={25} waste={true} />);
    expect(container.textContent).toContain("Capacity Reservations");
    expect(container.textContent).toContain("consider downsizing");
}); });
