import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiUsageFcPanel } from "@/components/fleet-ai-usage-fc-panel";
describe("FleetAiUsageFcPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiUsageFcPanel forecasters={3} active={3} horizon={180} accuracy={95} growth={30} />);
    expect(container.textContent).toContain("Usage Forecast");
}); });
