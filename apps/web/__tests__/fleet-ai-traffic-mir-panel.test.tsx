import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTrafficMirPanel } from "@/components/fleet-ai-traffic-mir-panel";
describe("FleetAiTrafficMirPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTrafficMirPanel mirrors={3} active={3} mirrored={50000000} targets={10} overhead={1.5} />);
    expect(container.textContent).toContain("Traffic Mirror");
}); });
