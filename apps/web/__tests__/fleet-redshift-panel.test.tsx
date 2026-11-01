import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRedshiftPanel } from "@/components/fleet-redshift-panel";
describe("FleetRedshiftPanel", () => { it("renders", () => {
    const { container } = render(<FleetRedshiftPanel clusters={3} available={3} nodes={24} storagePct={55} />);
    expect(container.textContent).toContain("Redshift");
    expect(container.textContent).toContain("55%");
}); });
