import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMonitorV8Panel } from "@/components/fleet-ai-monitor-v8-panel";
describe("FleetAiMonitorV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiMonitorV8Panel monitors={5} active={5} services={20000} metrics={5000000} uptime={99.9999} />);
    expect(container.textContent).toContain("Monitor v8");
}); });
