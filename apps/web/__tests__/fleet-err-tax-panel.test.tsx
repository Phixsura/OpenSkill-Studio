import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetErrTaxPanel } from "@/components/fleet-err-tax-panel";
describe("FleetErrTaxPanel", () => { it("renders", () => {
    const { container } = render(<FleetErrTaxPanel total={100} causes={8} topCause="timeout" />);
    expect(container.textContent).toContain("Error Taxonomy");
    expect(container.textContent).toContain("timeout");
}); });
