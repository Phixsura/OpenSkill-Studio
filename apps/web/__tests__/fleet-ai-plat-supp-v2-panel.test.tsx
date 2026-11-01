import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatSuppV2Panel } from "@/components/fleet-ai-plat-supp-v2-panel";
describe("FleetAiPlatSuppV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatSuppV2Panel systems={3} active={3} tickets={1000} resolution={8} csat={4.9} slaMet={99.5} />);
    expect(container.textContent).toContain("AI Support v2");
}); });
