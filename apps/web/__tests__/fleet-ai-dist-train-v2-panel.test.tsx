import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDistTrainV2Panel } from "@/components/fleet-ai-dist-train-v2-panel";
describe("FleetAiDistTrainV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDistTrainV2Panel trainers={5} active={5} nodes={200} gpus={1600} efficiency={95} />);
    expect(container.textContent).toContain("Distributed Training v2");
}); });
