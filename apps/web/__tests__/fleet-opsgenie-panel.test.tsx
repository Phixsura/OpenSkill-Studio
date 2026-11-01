import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOpsgeniePanel } from "@/components/fleet-opsgenie-panel";
describe("FleetOpsgeniePanel", () => { it("renders", () => {
    const { container } = render(<FleetOpsgeniePanel teams={10} openAlerts={5} avgClose={15} withOnCall={10} />);
    expect(container.textContent).toContain("OpsGenie");
    expect(container.textContent).toContain("5 open");
}); });
