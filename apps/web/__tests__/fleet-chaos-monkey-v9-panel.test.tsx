import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetChaosMonkeyV9Panel } from "@/components/fleet-chaos-monkey-v9-panel";
describe("FleetChaosMonkeyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetChaosMonkeyV9Panel targets={20} terminated={5} />);
    expect(container.textContent).toContain("Chaos Monkey v9");
}); });
