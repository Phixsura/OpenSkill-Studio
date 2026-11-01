import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiHealthDashPanel } from "@/components/fleet-ai-health-dash-panel";
describe("FleetAiHealthDashPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiHealthDashPanel dashboards={2} active={2} services={500} healthy={498} alerts={2} healthPct={99.6} />);
    expect(container.textContent).toContain("Health Dashboard");
}); });
