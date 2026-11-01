import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatCdV2Panel } from "@/components/fleet-ai-plat-cd-v2-panel";
describe("FleetAiPlatCdV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatCdV2Panel pipelines={4} active={4} deploys={1000} rollbacks={0} leadTime={3} />);
    expect(container.textContent).toContain("AI CD v2");
}); });
