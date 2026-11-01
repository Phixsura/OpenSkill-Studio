import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAbResultPanel } from "@/components/fleet-ab-result-panel";
describe("FleetAbResultPanel", () => { it("renders", () => {
    const { container } = render(<FleetAbResultPanel total={10} winners={4} losers={3} inconclusive={3} winRate={40} />);
    expect(container.textContent).toContain("A/B Results");
    expect(container.textContent).toContain("40% win rate");
}); });
