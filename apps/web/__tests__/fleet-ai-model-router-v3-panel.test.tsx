import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelRouterV3Panel } from "@/components/fleet-ai-model-router-v3-panel";
describe("FleetAiModelRouterV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelRouterV3Panel routers={4} active={4} models={100} routes={500000000} optimal={98} />);
    expect(container.textContent).toContain("Model Router v3");
}); });
