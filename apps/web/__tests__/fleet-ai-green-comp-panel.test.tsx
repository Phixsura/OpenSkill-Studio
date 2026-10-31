import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGreenCompPanel } from "@/components/fleet-ai-green-comp-panel";
describe("FleetAiGreenCompPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiGreenCompPanel trackers={4} active={4} co2={100} kwh={1000} renewable={95} />);
    expect(container.textContent).toContain("Green Computing");
}); });
