import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiLbPanel } from "@/components/fleet-ai-lb-panel";
describe("FleetAiLbPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiLbPanel balancers={5} active={5} rps={500000} backends={50} />);
    expect(container.textContent).toContain("AI Load Balancer");
}); });
