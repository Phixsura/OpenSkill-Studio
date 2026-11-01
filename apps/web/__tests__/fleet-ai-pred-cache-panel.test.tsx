import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPredCachePanel } from "@/components/fleet-ai-pred-cache-panel";
describe("FleetAiPredCachePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPredCachePanel caches={5} active={5} entries={200000000} hitRate={72} savedMs={300} />);
    expect(container.textContent).toContain("Prediction Cache");
}); });
