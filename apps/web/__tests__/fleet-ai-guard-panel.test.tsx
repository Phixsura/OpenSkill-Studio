import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGuardPanel } from "@/components/fleet-ai-guard-panel";
describe("FleetAiGuardPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiGuardPanel services={5} active={5} checks={500000} blocked={2500} blockRate={0.5} />);
    expect(container.textContent).toContain("AI Guardrails");
}); });
