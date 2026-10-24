import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRlPanel } from "@/components/fleet-ai-rl-panel";
describe("FleetAiRlPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRlPanel environments={3} active={3} episodes={5000000} reward={0.92} convergence={0.97} />);
    expect(container.textContent).toContain("Reinforcement Learning");
}); });
