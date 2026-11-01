import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetToilPanel } from "@/components/fleet-toil-panel";
describe("FleetToilPanel", () => { it("renders", () => {
    const { container } = render(<FleetToilPanel toilHours={30} engHours={70} toilPct={30} acceptable={true} />);
    expect(container.textContent).toContain("Toil Budget");
    expect(container.textContent).toContain("30% toil");
}); });
