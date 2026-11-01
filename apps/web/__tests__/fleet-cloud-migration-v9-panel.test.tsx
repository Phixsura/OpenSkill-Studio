import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCloudMigrationV9Panel } from "@/components/fleet-cloud-migration-v9-panel";
describe("FleetCloudMigrationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCloudMigrationV9Panel total={100} migrated={95} />);
    expect(container.textContent).toContain("Cloud Migration v9");
}); });
