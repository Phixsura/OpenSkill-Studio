import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRouterEngPanel } from "@/components/fleet-ai-router-eng-panel";
describe("FleetAiRouterEngPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRouterEngPanel routers={3} active={3} routes={50000000} models={50} savings={42} />);
    expect(container.textContent).toContain("Routing Engine");
}); });
