import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPrefectPanel } from "@/components/fleet-prefect-panel";
describe("FleetPrefectPanel", () => { it("renders", () => {
    const { container } = render(<FleetPrefectPanel deployments={20} active={18} completed={500} failed={5} />);
    expect(container.textContent).toContain("Prefect");
}); });
