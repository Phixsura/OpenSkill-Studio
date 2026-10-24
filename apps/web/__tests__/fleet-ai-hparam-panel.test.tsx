import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiHparamPanel } from "@/components/fleet-ai-hparam-panel";
describe("FleetAiHparamPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiHparamPanel tuners={5} active={5} trials={5000} bestScore={99.2} dimensions={30} />);
    expect(container.textContent).toContain("Hyperparameter Tuning");
}); });
