import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetObsCostPanel } from "@/components/fleet-obs-cost-panel";
describe("FleetObsCostPanel", () => { it("renders", () => {
    const { container } = render(<FleetObsCostPanel totalMonthly={12000} expensive={true} />);
    expect(container.textContent).toContain("Observability Cost");
    expect(container.textContent).toContain("High observability");
}); });
