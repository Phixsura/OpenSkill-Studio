import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatGrowthPanel } from "@/components/fleet-ai-plat-growth-panel";
describe("FleetAiPlatGrowthPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatGrowthPanel trackers={2} active={2} mau={5000000} mrr={20000000} growth={40} churn={1.5} />);
    expect(container.textContent).toContain("Platform Growth");
}); });
