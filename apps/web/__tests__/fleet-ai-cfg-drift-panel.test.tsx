import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCfgDriftPanel } from "@/components/fleet-ai-cfg-drift-panel";
describe("FleetAiCfgDriftPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCfgDriftPanel detectors={4} active={4} resources={5000} drifts={15} remediated={15} />);
    expect(container.textContent).toContain("Config Drift");
}); });
