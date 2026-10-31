import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiScalingV8Panel } from "@/components/fleet-ai-scaling-v8-panel";
describe("FleetAiScalingV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiScalingV8Panel scalers={5} active={5} replicas={100000} events={10000} predAcc={99} />);
    expect(container.textContent).toContain("Scaling v8");
}); });
