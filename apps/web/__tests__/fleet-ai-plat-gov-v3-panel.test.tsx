import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatGovV3Panel } from "@/components/fleet-ai-plat-gov-v3-panel";
describe("FleetAiPlatGovV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatGovV3Panel frameworks={3} active={3} policies={1000} reviews={500} compliance={99.8} />);
    expect(container.textContent).toContain("Governance v3");
}); });
