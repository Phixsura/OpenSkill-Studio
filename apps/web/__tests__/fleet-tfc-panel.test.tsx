import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTfcPanel } from "@/components/fleet-tfc-panel";
describe("FleetTfcPanel", () => { it("renders", () => {
    const { container } = render(<FleetTfcPanel total={20} applied={18} errored={2} monthlyCost={50000} />);
    expect(container.textContent).toContain("Terraform Cloud");
}); });
