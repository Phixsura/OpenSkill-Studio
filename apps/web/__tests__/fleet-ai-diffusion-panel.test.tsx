import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDiffusionPanel } from "@/components/fleet-ai-diffusion-panel";
describe("FleetAiDiffusionPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDiffusionPanel models={5} active={5} generations={5000000} steps={25} fid={6.2} />);
    expect(container.textContent).toContain("Diffusion Model");
}); });
