import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatFinalePanel } from "@/components/fleet-ai-plat-finale-panel";
describe("FleetAiPlatFinalePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatFinalePanel />);
    expect(container.textContent).toContain("GRAND FINALE");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
