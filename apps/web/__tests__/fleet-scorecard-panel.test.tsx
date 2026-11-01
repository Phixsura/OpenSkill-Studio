import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetScorecardPanel } from "@/components/fleet-scorecard-panel";
describe("FleetScorecardPanel", () => { it("renders", () => {
    const { container } = render(<FleetScorecardPanel dimensions={6} avgScore={90} top="reliability" bottom="cost" grade="A" />);
    expect(container.textContent).toContain("Platform Scorecard");
    expect(container.textContent).toContain("90 — A");
}); });
