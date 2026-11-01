import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatCdnV2Panel } from "@/components/fleet-ai-plat-cdn-v2-panel";
describe("FleetAiPlatCdnV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatCdnV2Panel cdns={3} active={3} pops={500} bandwidth={10000} cacheHit={98} />);
    expect(container.textContent).toContain("AI CDN v2");
}); });
