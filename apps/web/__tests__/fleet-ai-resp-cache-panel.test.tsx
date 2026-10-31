import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRespCachePanel } from "@/components/fleet-ai-resp-cache-panel";
describe("FleetAiRespCachePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRespCachePanel caches={5} active={5} entries={50000000} hitRate={80} tokensSaved={200000000000} />);
    expect(container.textContent).toContain("Response Cache");
}); });
