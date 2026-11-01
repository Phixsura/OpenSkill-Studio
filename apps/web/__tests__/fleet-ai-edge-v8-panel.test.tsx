import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEdgeV8Panel } from "@/components/fleet-ai-edge-v8-panel";
describe("FleetAiEdgeV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiEdgeV8Panel edges={10} active={10} locations={500} requests={50000000000} p50={1} />);
    expect(container.textContent).toContain("Edge v8");
}); });
