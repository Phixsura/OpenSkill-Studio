import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiWhRouterV2Panel } from "@/components/fleet-ai-wh-router-v2-panel";
describe("FleetAiWhRouterV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiWhRouterV2Panel routers={4} active={4} webhooks={2000} routed={50000000} retrySuccess={99.5} />);
    expect(container.textContent).toContain("Webhook Router v2");
}); });
