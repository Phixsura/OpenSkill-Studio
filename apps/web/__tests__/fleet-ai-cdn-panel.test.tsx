import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCdnPanel } from "@/components/fleet-ai-cdn-panel";
describe("FleetAiCdnPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCdnPanel cdns={3} active={3} pops={400} bandwidth={2000} cacheHit={97} />);
    expect(container.textContent).toContain("AI CDN");
}); });
