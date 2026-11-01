import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEdaPanel } from "@/components/fleet-eda-panel";
describe("FleetEdaPanel", () => { it("renders", () => {
    const { container } = render(<FleetEdaPanel topics={20} healthy={18} unhealthy={2} totalEps={5000} allHealthy={false} />);
    expect(container.textContent).toContain("Event-Driven");
    expect(container.textContent).toContain("2 lagging");
}); });
