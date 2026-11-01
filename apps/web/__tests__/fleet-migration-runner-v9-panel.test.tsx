import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMigrationRunnerV9Panel } from "@/components/fleet-migration-runner-v9-panel";
describe("FleetMigrationRunnerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetMigrationRunnerV9Panel total={50} pending={0} />);
    expect(container.textContent).toContain("Migration Runner v9");
}); });
