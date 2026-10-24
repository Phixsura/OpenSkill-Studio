import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAlertingEngineV9Panel } from "@/components/fleet-alerting-engine-v9-panel";
describe("FleetAlertingEngineV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetAlertingEngineV9Panel total={100} firing={0} />);
    expect(container.textContent).toContain("Alerting Engine v9");
}); });
