import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDxScorePanel } from "@/components/fleet-dx-score-panel";
describe("FleetDxScorePanel", () => { it("renders", () => {
    const { container } = render(<FleetDxScorePanel score={87.5} grade="B" />);
    expect(container.textContent).toContain("Developer Experience");
    expect(container.textContent).toContain("87.5 — B");
}); });
