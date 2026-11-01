import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatSumPanel } from "@/components/fleet-ai-plat-sum-panel";
describe("FleetAiPlatSumPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatSumPanel services={1000} healthy={1000} requests={5000000000} uptime={99.999} status="🟢 ALL SYSTEMS OPERATIONAL" />);
    expect(container.textContent).toContain("Platform Summary");
}); });
