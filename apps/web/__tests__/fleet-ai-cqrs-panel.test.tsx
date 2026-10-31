import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCqrsPanel } from "@/components/fleet-ai-cqrs-panel";
describe("FleetAiCqrsPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCqrsPanel handlers={4} active={4} commands={50000000} queries={500000000} cmdMs={10} />);
    expect(container.textContent).toContain("AI CQRS");
}); });
