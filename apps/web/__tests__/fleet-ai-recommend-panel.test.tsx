import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRecommendPanel } from "@/components/fleet-ai-recommend-panel";
describe("FleetAiRecommendPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRecommendPanel engines={4} active={4} requests={100000000} ctr={15} items={5000000} />);
    expect(container.textContent).toContain("Recommendations");
}); });
