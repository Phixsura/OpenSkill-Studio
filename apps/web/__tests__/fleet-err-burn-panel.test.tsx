import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetErrBurnPanel } from "@/components/fleet-err-burn-panel";
describe("FleetErrBurnPanel", () => { it("renders", () => {
    const { container } = render(<FleetErrBurnPanel total={5} fastBurn={1} slowBurn={2} alert={true} />);
    expect(container.textContent).toContain("Error Budget Burn");
    expect(container.textContent).toContain("Fast burn detected");
}); });
