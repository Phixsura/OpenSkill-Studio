import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCapacityPanel } from "@/components/fleet-ai-capacity-panel";
describe("FleetAiCapacityPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCapacityPanel plans={5} active={5} forecastDays={90} utilization={60} headroom={40} />);
    expect(container.textContent).toContain("Capacity Planning");
}); });
