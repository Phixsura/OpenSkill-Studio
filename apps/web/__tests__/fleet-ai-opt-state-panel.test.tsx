import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiOptStatePanel } from "@/components/fleet-ai-opt-state-panel";
describe("FleetAiOptStatePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiOptStatePanel managers={3} active={3} states={10000} storageGb={1000} restorations={500} />);
    expect(container.textContent).toContain("Optimizer State");
}); });
