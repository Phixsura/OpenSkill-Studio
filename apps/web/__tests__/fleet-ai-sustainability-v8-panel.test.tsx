import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSustainabilityV8Panel } from "@/components/fleet-ai-sustainability-v8-panel";
describe("FleetAiSustainabilityV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiSustainabilityV8Panel trackers={3} active={3} carbon={10000} renewable={99} pue={1.02} />);
    expect(container.textContent).toContain("Sustainability v8");
}); });
