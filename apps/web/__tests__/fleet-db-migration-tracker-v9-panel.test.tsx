import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDbMigrationTrackerV9Panel } from "@/components/fleet-db-migration-tracker-v9-panel";
describe("FleetDbMigrationTrackerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDbMigrationTrackerV9Panel envs={4} pending={0} />);
    expect(container.textContent).toContain("DB Migration Tracker v9");
}); });
