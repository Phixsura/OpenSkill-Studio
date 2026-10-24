import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiHybridSrchPanel } from "@/components/fleet-ai-hybrid-srch-panel";
describe("FleetAiHybridSrchPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiHybridSrchPanel engines={4} active={4} queries={50000000} mrr={0.95} docs={2000000000} />);
    expect(container.textContent).toContain("Hybrid Search");
}); });
