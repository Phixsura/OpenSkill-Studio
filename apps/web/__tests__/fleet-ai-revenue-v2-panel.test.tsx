import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRevenueV2Panel } from "@/components/fleet-ai-revenue-v2-panel";
describe("FleetAiRevenueV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiRevenueV2Panel trackers={2} active={2} mrr={50000000} arr={600000000} growth={40} ndr={140} />);
    expect(container.textContent).toContain("Revenue v2");
}); });
