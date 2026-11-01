import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatAnalPanel } from "@/components/fleet-ai-plat-anal-panel";
describe("FleetAiPlatAnalPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatAnalPanel dashboards={2} active={2} dau={500000} mau={2000000} apiCalls={5000000000} revenue={500000} />);
    expect(container.textContent).toContain("Platform Analytics");
}); });
