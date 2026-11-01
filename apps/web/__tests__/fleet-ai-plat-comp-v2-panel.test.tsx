import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatCompV2Panel } from "@/components/fleet-ai-plat-comp-v2-panel";
describe("FleetAiPlatCompV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatCompV2Panel frameworks={3} active={3} certifications={["SOC2", "GDPR"]} controls={1000} compliance={99.5} />);
    expect(container.textContent).toContain("Compliance v2");
}); });
