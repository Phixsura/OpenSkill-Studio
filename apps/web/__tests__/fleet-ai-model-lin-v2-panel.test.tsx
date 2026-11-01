import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelLinV2Panel } from "@/components/fleet-ai-model-lin-v2-panel";
describe("FleetAiModelLinV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelLinV2Panel trackers={3} active={3} models={1000} depth={15} datasets={2000} />);
    expect(container.textContent).toContain("Model Lineage v2");
}); });
