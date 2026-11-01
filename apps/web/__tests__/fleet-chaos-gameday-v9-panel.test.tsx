import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetChaosGamedayV9Panel } from "@/components/fleet-chaos-gameday-v9-panel";
describe("FleetChaosGamedayV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetChaosGamedayV9Panel gamedays={10} findings={25} />);
    expect(container.textContent).toContain("Chaos GameDay v9");
}); });
