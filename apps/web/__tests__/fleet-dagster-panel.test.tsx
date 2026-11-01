import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDagsterPanel } from "@/components/fleet-dagster-panel";
describe("FleetDagsterPanel", () => { it("renders", () => {
    const { container } = render(<FleetDagsterPanel deployments={5} running={5} assets={500} materializations={10000} />);
    expect(container.textContent).toContain("Dagster");
    expect(container.textContent).toContain("500 assets");
}); });
