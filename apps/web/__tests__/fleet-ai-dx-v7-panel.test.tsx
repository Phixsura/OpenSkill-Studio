import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDxV7Panel } from "@/components/fleet-ai-dx-v7-panel";
describe("FleetAiDxV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDxV7Panel trackers={3} active={3} nps={85} ttfc={2} docs={99} sdk={90} />);
    expect(container.textContent).toContain("Developer Experience v7");
}); });
