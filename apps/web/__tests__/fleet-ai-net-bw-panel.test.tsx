import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiNetBwPanel } from "@/components/fleet-ai-net-bw-panel";
describe("FleetAiNetBwPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiNetBwPanel monitors={5} active={5} ingress={200} egress={400} utilization={55} />);
    expect(container.textContent).toContain("Network Bandwidth");
}); });
