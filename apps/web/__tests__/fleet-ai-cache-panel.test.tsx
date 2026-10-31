import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCachePanel } from "@/components/fleet-ai-cache-panel";
describe("FleetAiCachePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCachePanel caches={5} active={5} hitRate={45} tokensSaved={500000000} costSaved={2500} />);
    expect(container.textContent).toContain("AI Cache");
}); });
