import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiChaosV8Panel } from "@/components/fleet-ai-chaos-v8-panel";
describe("FleetAiChaosV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiChaosV8Panel systems={5} active={5} experiments={5000} recovery={5} blast={2} />);
    expect(container.textContent).toContain("Chaos v8");
}); });
