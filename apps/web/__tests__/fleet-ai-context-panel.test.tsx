import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiContextPanel } from "@/components/fleet-ai-context-panel";
describe("FleetAiContextPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiContextPanel services={5} active={5} avgUtil={60} truncations={500} />);
    expect(container.textContent).toContain("AI Context");
}); });
