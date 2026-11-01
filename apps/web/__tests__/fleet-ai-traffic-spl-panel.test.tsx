import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTrafficSplPanel } from "@/components/fleet-ai-traffic-spl-panel";
describe("FleetAiTrafficSplPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTrafficSplPanel splitters={4} active={4} splits={20} requests={500000000} variants={5} />);
    expect(container.textContent).toContain("Traffic Split");
}); });
