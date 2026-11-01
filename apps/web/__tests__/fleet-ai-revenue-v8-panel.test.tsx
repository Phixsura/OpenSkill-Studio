import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRevenueV8Panel } from "@/components/fleet-ai-revenue-v8-panel";
describe("FleetAiRevenueV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiRevenueV8Panel trackers={3} active={3} mrr={500000000} ndr={150} margin={85} />);
    expect(container.textContent).toContain("Revenue v8");
}); });
