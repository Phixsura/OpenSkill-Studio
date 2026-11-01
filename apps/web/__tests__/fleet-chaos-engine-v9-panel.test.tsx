import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetChaosEngineV9Panel } from "@/components/fleet-chaos-engine-v9-panel";
describe("FleetChaosEngineV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetChaosEngineV9Panel experiments={50} completed={48} />);
    expect(container.textContent).toContain("Chaos Engine v9");
}); });
