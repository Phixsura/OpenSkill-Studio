import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatOverviewPanel } from "@/components/fleet-ai-plat-overview-panel";
describe("FleetAiPlatOverviewPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatOverviewPanel services={5000} healthy={5000} models={2000} requests={100000000000} uptime={99.999} revenue={50000000} status="🟢 ALL OPERATIONAL" />);
    expect(container.textContent).toContain("Platform Overview");
}); });
