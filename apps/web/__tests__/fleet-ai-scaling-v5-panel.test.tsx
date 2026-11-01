import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiScalingV5Panel } from "@/components/fleet-ai-scaling-v5-panel";
describe("FleetAiScalingV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiScalingV5Panel scalers={5} active={5} replicas={10000} events={2000} predAcc={97} />);
    expect(container.textContent).toContain("Scaling v5");
}); });
