import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTechDebtPanel } from "@/components/fleet-tech-debt-panel";
describe("FleetTechDebtPanel", () => { it("renders", () => {
    const { container } = render(<FleetTechDebtPanel totalDebt={200} highDebt={1} avgPerService={40} manageable={true} />);
    expect(container.textContent).toContain("Tech Debt");
    expect(container.textContent).toContain("Manageable");
}); });
