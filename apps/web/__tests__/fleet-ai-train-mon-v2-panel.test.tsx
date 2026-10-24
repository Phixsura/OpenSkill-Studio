import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTrainMonV2Panel } from "@/components/fleet-ai-train-mon-v2-panel";
describe("FleetAiTrainMonV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiTrainMonV2Panel monitors={4} active={4} jobs={500} metrics={10000} alerts={15} />);
    expect(container.textContent).toContain("Training Monitor v2");
}); });
