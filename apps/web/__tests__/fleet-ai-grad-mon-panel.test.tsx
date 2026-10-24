import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGradMonPanel } from "@/components/fleet-ai-grad-mon-panel";
describe("FleetAiGradMonPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiGradMonPanel monitors={4} active={4} jobs={100} vanishing={0} exploding={0} healthy={100} />);
    expect(container.textContent).toContain("Gradient Monitor");
}); });
