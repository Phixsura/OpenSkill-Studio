import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiConvRouterPanel } from "@/components/fleet-ai-conv-router-panel";
describe("FleetAiConvRouterPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiConvRouterPanel routers={4} active={4} conversations={10000000} models={20} optimalPct={95} />);
    expect(container.textContent).toContain("Conversation Router");
}); });
