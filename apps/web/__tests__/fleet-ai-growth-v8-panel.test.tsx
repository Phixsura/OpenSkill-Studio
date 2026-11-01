import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGrowthV8Panel } from "@/components/fleet-ai-growth-v8-panel";
describe("FleetAiGrowthV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiGrowthV8Panel trackers={3} active={3} mau={50000000} arr={5000000000} growth={70} />);
    expect(container.textContent).toContain("Growth v8");
}); });
