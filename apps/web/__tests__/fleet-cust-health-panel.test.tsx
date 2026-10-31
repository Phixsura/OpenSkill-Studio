import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCustHealthPanel } from "@/components/fleet-cust-health-panel";
describe("FleetCustHealthPanel", () => { it("renders", () => {
    const { container } = render(<FleetCustHealthPanel total={100} healthy={70} atRisk={20} churning={10} healthRate={70} />);
    expect(container.textContent).toContain("Customer Health");
    expect(container.textContent).toContain("70% healthy");
}); });
