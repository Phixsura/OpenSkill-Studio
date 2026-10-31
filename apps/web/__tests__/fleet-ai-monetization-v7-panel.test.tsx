import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMonetizationV7Panel } from "@/components/fleet-ai-monetization-v7-panel";
describe("FleetAiMonetizationV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiMonetizationV7Panel trackers={2} active={2} mrr={200000000} arpu={1000} ltv={100000} payback={4} />);
    expect(container.textContent).toContain("Monetization v7");
}); });
