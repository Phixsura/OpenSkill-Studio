import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCacheLayerPanel } from "@/components/fleet-ai-cache-layer-panel";
describe("FleetAiCacheLayerPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCacheLayerPanel caches={4} active={4} hitRate={82} entries={20000000} savedTokens={50000000000} />);
    expect(container.textContent).toContain("Cache Layer");
}); });
