import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiScaleV7Panel } from "@/components/fleet-ai-scale-v7-panel";
describe("FleetAiScaleV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiScaleV7Panel systems={5} active={5} peakRps={500000000} gpus={200000} dataPb={5000} users={200000000} />);
    expect(container.textContent).toContain("Scale v7");
}); });
