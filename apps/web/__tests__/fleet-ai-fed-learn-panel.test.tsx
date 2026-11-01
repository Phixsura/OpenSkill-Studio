import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiFedLearnPanel } from "@/components/fleet-ai-fed-learn-panel";
describe("FleetAiFedLearnPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiFedLearnPanel clusters={5} active={5} participants={500} rounds={2000} convergence={0.99} />);
    expect(container.textContent).toContain("Federated Learning");
}); });
