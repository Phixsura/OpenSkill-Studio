import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetChaosMonkeyPanel } from "@/components/fleet-chaos-monkey-panel";
describe("FleetChaosMonkeyPanel", () => { it("renders", () => {
    const { container } = render(<FleetChaosMonkeyPanel enabled={true} terminated={10} survived={9} survivalRate={90} />);
    expect(container.textContent).toContain("Chaos Monkey");
    expect(container.textContent).toContain("90% survived");
}); });
