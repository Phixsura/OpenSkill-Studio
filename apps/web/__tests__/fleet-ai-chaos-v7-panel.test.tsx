import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiChaosV7Panel } from "@/components/fleet-ai-chaos-v7-panel";
describe("FleetAiChaosV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiChaosV7Panel systems={5} active={5} experiments={1000} blast={3} recovery={5} />);
    expect(container.textContent).toContain("Chaos v7");
}); });
