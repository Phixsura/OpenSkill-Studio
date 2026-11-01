import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiQualityGatePanel } from "@/components/fleet-ai-quality-gate-panel";
describe("FleetAiQualityGatePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiQualityGatePanel gates={5} active={5} evals={1000} passed={960} blocked={40} checks={25} />);
    expect(container.textContent).toContain("Quality Gate");
}); });
