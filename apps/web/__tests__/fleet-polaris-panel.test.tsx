import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPolarisPanel } from "@/components/fleet-polaris-panel";
describe("FleetPolarisPanel", () => { it("renders", () => {
    const { container } = render(<FleetPolarisPanel total={100} score={90} warnings={5} dangers={2} grade="A" />);
    expect(container.textContent).toContain("Polaris");
    expect(container.textContent).toContain("90% — A");
}); });
