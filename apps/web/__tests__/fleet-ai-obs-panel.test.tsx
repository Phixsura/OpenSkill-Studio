import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiObsPanel } from "@/components/fleet-ai-obs-panel";
describe("FleetAiObsPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiObsPanel instances={5} active={5} traces={5000000} spans={25000000} />);
    expect(container.textContent).toContain("AI Observability");
}); });
