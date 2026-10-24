import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatResV3Panel } from "@/components/fleet-ai-plat-res-v3-panel";
describe("FleetAiPlatResV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatResV3Panel systems={5} active={5} blastRadius={3} recovery={15} chaosScore={98} />);
    expect(container.textContent).toContain("Resilience v3");
}); });
