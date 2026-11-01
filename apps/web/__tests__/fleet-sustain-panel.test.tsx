import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSustainPanel } from "@/components/fleet-sustain-panel";
describe("FleetSustainPanel", () => { it("renders", () => {
    const { container } = render(<FleetSustainPanel carbonKg={500} renewablePct={95} pue={1.1} grade="A" />);
    expect(container.textContent).toContain("Sustainability");
    expect(container.textContent).toContain("Grade A");
}); });
