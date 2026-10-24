import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiLbV4Panel } from "@/components/fleet-ai-lb-v4-panel";
describe("FleetAiLbV4Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiLbV4Panel balancers={5} active={5} backends={200} rps={50000000} hc={3} />);
    expect(container.textContent).toContain("Load Balancer v4");
}); });
