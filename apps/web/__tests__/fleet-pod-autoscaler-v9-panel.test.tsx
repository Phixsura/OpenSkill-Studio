import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPodAutoscalerV9Panel } from "@/components/fleet-pod-autoscaler-v9-panel";
describe("FleetPodAutoscalerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetPodAutoscalerV9Panel autoscalers={30} events={50} />);
    expect(container.textContent).toContain("Pod Autoscaler v9");
}); });
