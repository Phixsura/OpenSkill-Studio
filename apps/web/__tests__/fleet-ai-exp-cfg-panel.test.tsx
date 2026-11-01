import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiExpCfgPanel } from "@/components/fleet-ai-exp-cfg-panel";
describe("FleetAiExpCfgPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiExpCfgPanel managers={4} active={4} configs={2000} templates={80} overrides={500} />);
    expect(container.textContent).toContain("Experiment Config");
}); });
