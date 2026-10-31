import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetChurnPanel } from "@/components/fleet-churn-panel";
describe("FleetChurnPanel", () => { it("renders", () => {
    const { container } = render(<FleetChurnPanel churned={10} churnRate={10} netGrowth={10} healthy={false} />);
    expect(container.textContent).toContain("Churn Rate");
    expect(container.textContent).toContain("10%");
}); });
