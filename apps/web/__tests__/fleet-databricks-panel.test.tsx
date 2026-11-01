import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDatabricksPanel } from "@/components/fleet-databricks-panel";
describe("FleetDatabricksPanel", () => { it("renders", () => {
    const { container } = render(<FleetDatabricksPanel workspaces={3} active={3} clusters={15} dbu={1500} />);
    expect(container.textContent).toContain("Databricks");
    expect(container.textContent).toContain("15 clusters");
}); });
