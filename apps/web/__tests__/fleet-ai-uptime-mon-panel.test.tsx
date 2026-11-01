import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiUptimeMonPanel } from "@/components/fleet-ai-uptime-mon-panel";
describe("FleetAiUptimeMonPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiUptimeMonPanel monitors={5} active={5} endpoints={500} uptime={99.999} checks={5000000} />);
    expect(container.textContent).toContain("Uptime Monitor");
}); });
