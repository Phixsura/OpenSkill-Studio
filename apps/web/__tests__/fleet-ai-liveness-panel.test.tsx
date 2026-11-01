import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiLivenessPanel } from "@/components/fleet-ai-liveness-panel";
describe("FleetAiLivenessPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiLivenessPanel checkers={5} active={5} services={1000} alive={1000} restarts={1} />);
    expect(container.textContent).toContain("AI Liveness");
}); });
