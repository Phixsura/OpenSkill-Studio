import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiMigrationGuideV9Panel } from "@/components/fleet-api-migration-guide-v9-panel";
describe("FleetApiMigrationGuideV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiMigrationGuideV9Panel migrations={10} completed={8} />);
    expect(container.textContent).toContain("Migration Guide v9");
}); });
