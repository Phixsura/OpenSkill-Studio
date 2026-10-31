import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiUsageAnalPanel } from "@/components/fleet-ai-usage-anal-panel";
describe("FleetAiUsageAnalPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiUsageAnalPanel dashboards={3} active={3} dau={500000} requests={200000000} retention={90} />);
    expect(container.textContent).toContain("Usage Analytics");
}); });
