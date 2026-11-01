import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiLbV2Panel } from "@/components/fleet-ai-lb-v2-panel";
describe("FleetAiLbV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiLbV2Panel balancers={5} active={5} backends={50} rps={2000000} algorithms={["least_connections"]} />);
    expect(container.textContent).toContain("Load Balancer");
}); });
