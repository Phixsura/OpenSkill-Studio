import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEdgeInfPanel } from "@/components/fleet-ai-edge-inf-panel";
describe("FleetAiEdgeInfPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiEdgeInfPanel edges={20} active={20} locations={15} requests={100000000} p50={5} />);
    expect(container.textContent).toContain("Edge Inference");
}); });
