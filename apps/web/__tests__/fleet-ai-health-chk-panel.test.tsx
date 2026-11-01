import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiHealthChkPanel } from "@/components/fleet-ai-health-chk-panel";
describe("FleetAiHealthChkPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiHealthChkPanel probes={20} healthy={20} degraded={0} down={0} latency={6} />);
    expect(container.textContent).toContain("Health Check");
}); });
