import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRouterPanel } from "@/components/fleet-ai-router-panel";
describe("FleetAiRouterPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRouterPanel routers={5} active={5} requests={25000000} models={20} fallbackPct={3} />);
    expect(container.textContent).toContain("AI Router");
}); });
