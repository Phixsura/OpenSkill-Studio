import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLeadTimePanel } from "@/components/fleet-lead-time-panel";
describe("FleetLeadTimePanel", () => { it("renders", () => {
    const { container } = render(<FleetLeadTimePanel total={20} avgLeadTime={45} underHour={15} elite={true} />);
    expect(container.textContent).toContain("Lead Time");
    expect(container.textContent).toContain("Elite performance");
}); });
