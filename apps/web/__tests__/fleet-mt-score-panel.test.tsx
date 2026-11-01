import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMtScorePanel } from "@/components/fleet-mt-score-panel";
describe("FleetMtScorePanel", () => { it("renders", () => {
    const { container } = render(<FleetMtScorePanel score={90} data={95} compute={90} network={85} enterpriseReady={true} />);
    expect(container.textContent).toContain("Multitenancy");
    expect(container.textContent).toContain("90%");
}); });
