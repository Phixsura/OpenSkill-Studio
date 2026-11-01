import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatEdgeV2Panel } from "@/components/fleet-ai-plat-edge-v2-panel";
describe("FleetAiPlatEdgeV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatEdgeV2Panel edges={5} active={5} locations={100} requests={5000000000} p50={3} />);
    expect(container.textContent).toContain("AI Edge v2");
}); });
