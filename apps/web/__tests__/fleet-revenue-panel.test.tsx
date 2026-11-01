import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRevenuePanel } from "@/components/fleet-revenue-panel";
describe("FleetRevenuePanel", () => { it("renders", () => {
    const { container } = render(<FleetRevenuePanel mrr={50000} arr={600000} mrrGrowth={15} ltvCacRatio={4} unitHealthy={true} />);
    expect(container.textContent).toContain("Revenue");
    expect(container.textContent).toContain("$600,000");
}); });
