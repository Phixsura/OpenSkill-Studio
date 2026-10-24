import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiKgPanel } from "@/components/fleet-ai-kg-panel";
describe("FleetAiKgPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiKgPanel graphs={2} active={2} entities={5000000} relations={20000000} queries={1000000} />);
    expect(container.textContent).toContain("Knowledge Graph");
}); });
