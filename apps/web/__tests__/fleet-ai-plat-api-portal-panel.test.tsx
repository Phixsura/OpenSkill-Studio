import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatApiPortalPanel } from "@/components/fleet-ai-plat-api-portal-panel";
describe("FleetAiPlatApiPortalPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatApiPortalPanel portals={3} active={3} apis={1000} pages={10000} developers={500000} apiKeys={1000000} />);
    expect(container.textContent).toContain("API Portal v2");
}); });
