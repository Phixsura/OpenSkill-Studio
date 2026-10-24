import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOncallPanel } from "@/components/fleet-oncall-panel";
describe("FleetOncallPanel", () => { it("renders", () => {
    const { container } = render(<FleetOncallPanel rotations={5} activeOncall={2} overloaded={1} healthy={false} />);
    expect(container.textContent).toContain("On-Call");
    expect(container.textContent).toContain("1 overloaded");
}); });
