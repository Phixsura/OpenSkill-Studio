import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAlertFatiguePanel } from "@/components/fleet-alert-fatigue-panel";
describe("FleetAlertFatiguePanel", () => { it("renders", () => {
    const { container } = render(<FleetAlertFatiguePanel total={100} actionable={25} noise={75} noisePct={75} fatiguing={true} />);
    expect(container.textContent).toContain("Alert Fatigue");
    expect(container.textContent).toContain("High alert fatigue");
}); });
