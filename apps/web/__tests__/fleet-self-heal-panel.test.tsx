import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSelfHealPanel } from "@/components/fleet-self-heal-panel";
describe("FleetSelfHealPanel", () => { it("renders", () => {
    const { container } = render(<FleetSelfHealPanel total={20} autoRecovered={16} manual={4} automationRate={80} mature={true} />);
    expect(container.textContent).toContain("Self-Healing");
    expect(container.textContent).toContain("80% auto");
}); });
