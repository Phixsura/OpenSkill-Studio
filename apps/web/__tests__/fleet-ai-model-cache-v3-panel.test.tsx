import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelCacheV3Panel } from "@/components/fleet-ai-model-cache-v3-panel";
describe("FleetAiModelCacheV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelCacheV3Panel caches={5} active={5} models={500} hitRate={95} memory={20000} />);
    expect(container.textContent).toContain("Model Cache v3");
}); });
