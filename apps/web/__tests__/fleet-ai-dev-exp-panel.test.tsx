import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDevExpPanel } from "@/components/fleet-ai-dev-exp-panel";
describe("FleetAiDevExpPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDevExpPanel trackers={3} active={3} nps={80} ttfc={3} docs={98} />);
    expect(container.textContent).toContain("Developer Experience");
}); });
