import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSustainabilityV7Panel } from "@/components/fleet-ai-sustainability-v7-panel";
describe("FleetAiSustainabilityV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiSustainabilityV7Panel trackers={3} active={3} carbon={2000} renewable={98} pue={1.05} />);
    expect(container.textContent).toContain("Sustainability v7");
}); });
