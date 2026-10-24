import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSpaceliftPanel } from "@/components/fleet-spacelift-panel";
describe("FleetSpaceliftPanel", () => { it("renders", () => {
    const { container } = render(<FleetSpaceliftPanel total={15} tracked={15} drifted={2} policies={20} />);
    expect(container.textContent).toContain("Spacelift");
    expect(container.textContent).toContain("2 drifted");
}); });
