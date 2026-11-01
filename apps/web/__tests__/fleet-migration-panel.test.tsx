import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMigrationPanel } from "@/components/fleet-migration-panel";
describe("FleetMigrationPanel", () => { it("renders", () => {
    const { container } = render(<FleetMigrationPanel total={5} current={3} pending={2} totalPending={5} allCurrent={false} />);
    expect(container.textContent).toContain("DB Migrations");
    expect(container.textContent).toContain("5 pending");
}); });
