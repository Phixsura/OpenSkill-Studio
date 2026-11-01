import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSeldonPanel } from "@/components/fleet-seldon-panel";
describe("FleetSeldonPanel", () => { it("renders", () => {
    const { container } = render(<FleetSeldonPanel deployments={10} available={10} predictors={20} requests={2000000} />);
    expect(container.textContent).toContain("Seldon");
}); });
