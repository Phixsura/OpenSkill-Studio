import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEnsembleV2Panel } from "@/components/fleet-ai-ensemble-v2-panel";
describe("FleetAiEnsembleV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiEnsembleV2Panel ensembles={4} active={4} avgModels={7} requests={20000000} boost={15} />);
    expect(container.textContent).toContain("Ensemble v2");
}); });
