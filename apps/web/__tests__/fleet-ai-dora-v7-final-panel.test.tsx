import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDoraV7FinalPanel } from "@/components/fleet-ai-dora-v7-final-panel";
describe("FleetAiDoraV7FinalPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDoraV7FinalPanel />);
    expect(container.textContent).toContain("DORA v7 FINAL");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
