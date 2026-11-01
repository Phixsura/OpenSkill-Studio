import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetChaosTestingV9Panel } from "@/components/fleet-chaos-testing-v9-panel";
describe("FleetChaosTestingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetChaosTestingV9Panel services={200} coverage={95} />);
    expect(container.textContent).toContain("Chaos Testing v9");
}); });
