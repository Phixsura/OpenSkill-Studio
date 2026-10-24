import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetScaleHistPanel } from "@/components/fleet-scale-hist-panel";
describe("FleetScaleHistPanel", () => { it("renders", () => {
    const { container } = render(<FleetScaleHistPanel total={10} scaleUps={7} scaleDowns={3} ratio={2.33} />);
    expect(container.textContent).toContain("Scaling History");
    expect(container.textContent).toContain("2.33x");
}); });
