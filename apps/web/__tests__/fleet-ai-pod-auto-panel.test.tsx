import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPodAutoPanel } from "@/components/fleet-ai-pod-auto-panel";
describe("FleetAiPodAutoPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPodAutoPanel scalers={5} active={5} pods={1000} targetCpu={75} scaleEvents={100} />);
    expect(container.textContent).toContain("Pod Autoscaler");
}); });
