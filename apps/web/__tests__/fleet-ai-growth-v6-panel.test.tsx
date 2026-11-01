import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGrowthV6Panel } from "@/components/fleet-ai-growth-v6-panel";
describe("FleetAiGrowthV6Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiGrowthV6Panel trackers={3} active={3} mau={20000000} arr={1000000000} growth={50} ndr={150} />);
    expect(container.textContent).toContain("Growth v6");
}); });
