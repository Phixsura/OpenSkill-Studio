import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHealthAggPanel } from "@/components/fleet-health-agg-panel";
describe("FleetHealthAggPanel", () => { it("renders", () => {
    const { container } = render(<FleetHealthAggPanel overallScore={85} dimensions={10} critical={0} status="healthy" />);
    expect(container.textContent).toContain("Fleet Health");
    expect(container.textContent).toContain("85");
}); });
