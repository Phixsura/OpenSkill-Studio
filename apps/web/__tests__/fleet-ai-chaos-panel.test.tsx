import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiChaosPanel } from "@/components/fleet-ai-chaos-panel";
describe("FleetAiChaosPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiChaosPanel experiments={10} active={10} runs={1000} failures={30} systems={50} />);
    expect(container.textContent).toContain("Chaos Engineering");
}); });
