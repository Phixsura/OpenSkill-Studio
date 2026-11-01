import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAutoscalePanel } from "@/components/fleet-ai-autoscale-panel";
describe("FleetAiAutoscalePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAutoscalePanel policies={8} active={8} scaleEvents={100} replicas={200} targetUtil={75} />);
    expect(container.textContent).toContain("Auto-Scaling");
}); });
