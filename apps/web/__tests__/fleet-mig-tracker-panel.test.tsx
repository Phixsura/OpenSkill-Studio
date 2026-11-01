import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMigTrackerPanel } from "@/components/fleet-mig-tracker-panel";
describe("FleetMigTrackerPanel", () => { it("renders", () => {
    const { container } = render(<FleetMigTrackerPanel total={5} completed={3} inProgress={1} blocked={1} allDone={false} />);
    expect(container.textContent).toContain("Migrations");
    expect(container.textContent).toContain("1 blocked");
}); });
