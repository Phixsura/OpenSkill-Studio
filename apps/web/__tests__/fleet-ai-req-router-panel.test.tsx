import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiReqRouterPanel } from "@/components/fleet-ai-req-router-panel";
describe("FleetAiReqRouterPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiReqRouterPanel routers={3} active={3} routes={200000000} strategies={["cost", "latency"]} optimalPct={97} />);
    expect(container.textContent).toContain("Request Router");
}); });
