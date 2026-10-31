import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPipelineLagPanel } from "@/components/fleet-pipeline-lag-panel";
describe("FleetPipelineLagPanel", () => { it("renders", () => {
    const { container } = render(<FleetPipelineLagPanel total={5} lagging={1} maxLag={30} fresh={false} />);
    expect(container.textContent).toContain("Pipeline Lag");
    expect(container.textContent).toContain("1 lagging");
}); });
