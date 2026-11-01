import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIncLearnPanel } from "@/components/fleet-inc-learn-panel";
describe("FleetIncLearnPanel", () => { it("renders", () => {
    const { container } = render(<FleetIncLearnPanel total={15} implemented={10} pending={5} learningRate={66.7} />);
    expect(container.textContent).toContain("Incident Learning");
    expect(container.textContent).toContain("5 lessons pending");
}); });
