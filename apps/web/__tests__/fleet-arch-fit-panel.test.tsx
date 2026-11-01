import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetArchFitPanel } from "@/components/fleet-arch-fit-panel";
describe("FleetArchFitPanel", () => { it("renders", () => {
    const { container } = render(<FleetArchFitPanel total={20} passing={18} failing={2} score={90} fit={true} />);
    expect(container.textContent).toContain("Architecture Fitness");
    expect(container.textContent).toContain("90%");
}); });
