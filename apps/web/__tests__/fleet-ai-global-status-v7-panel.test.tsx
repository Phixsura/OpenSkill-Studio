import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGlobalStatusV7Panel } from "@/components/fleet-ai-global-status-v7-panel";
describe("FleetAiGlobalStatusV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiGlobalStatusV7Panel regions={15} active={15} services={5000} healthy={5000} requests={200000000000} uptime={99.9999} status="🟢 ALL REGIONS OPERATIONAL" />);
    expect(container.textContent).toContain("Global Status v7");
}); });
