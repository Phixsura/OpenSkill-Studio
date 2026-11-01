import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAutoscaleV3Panel } from "@/components/fleet-ai-autoscale-v3-panel";
describe("FleetAiAutoscaleV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiAutoscaleV3Panel scalers={5} active={5} replicas={1000} events={500} predAcc={95} />);
    expect(container.textContent).toContain("Autoscaler v3");
}); });
