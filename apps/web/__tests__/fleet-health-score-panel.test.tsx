import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHealthScorePanel } from "@/components/fleet-health-score-panel";
describe("FleetHealthScorePanel", () => { it("renders", () => {
    const { container } = render(<FleetHealthScorePanel score={90} grade="A" services={10} />);
    expect(container.textContent).toContain("Fleet Health");
    expect(container.textContent).toContain("90 — A");
    expect(container.textContent).toContain("10 services");
}); });
