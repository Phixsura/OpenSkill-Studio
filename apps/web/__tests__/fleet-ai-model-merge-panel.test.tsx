import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelMergePanel } from "@/components/fleet-ai-model-merge-panel";
describe("FleetAiModelMergePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelMergePanel mergers={3} active={3} merges={200} methods={["SLERP", "TIES"]} improvement={15} />);
    expect(container.textContent).toContain("Model Merging");
}); });
