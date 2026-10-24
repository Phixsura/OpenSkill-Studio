import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMaintenanceWindowV9Panel } from "@/components/fleet-maintenance-window-v9-panel";
describe("FleetMaintenanceWindowV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetMaintenanceWindowV9Panel windows={10} upcoming={2} />);
    expect(container.textContent).toContain("Maintenance Window v9");
}); });
