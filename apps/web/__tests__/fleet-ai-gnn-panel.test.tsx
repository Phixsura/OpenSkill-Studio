import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGnnPanel } from "@/components/fleet-ai-gnn-panel";
describe("FleetAiGnnPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiGnnPanel models={4} active={4} nodes={500000000} edges={2000000000} accuracy={94} />);
    expect(container.textContent).toContain("Graph Neural Net");
}); });
