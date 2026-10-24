import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiInfCachePanel } from "@/components/fleet-ai-inf-cache-panel";
describe("FleetAiInfCachePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiInfCachePanel caches={5} active={5} entries={50000000} hitRate={72} costSaved={25000} />);
    expect(container.textContent).toContain("Inference Cache");
}); });
