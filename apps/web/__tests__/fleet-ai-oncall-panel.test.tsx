import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiOncallPanel } from "@/components/fleet-ai-oncall-panel";
describe("FleetAiOncallPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiOncallPanel schedulers={3} active={3} engineers={30} pages={20} ackMin={1.5} />);
    expect(container.textContent).toContain("On-Call");
}); });
