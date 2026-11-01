import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiShadowTstPanel } from "@/components/fleet-ai-shadow-tst-panel";
describe("FleetAiShadowTstPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiShadowTstPanel shadows={4} active={4} mirrored={8000000} divergence={1.5} />);
    expect(container.textContent).toContain("Shadow Testing");
}); });
