import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelDiffPanel } from "@/components/fleet-ai-model-diff-panel";
describe("FleetAiModelDiffPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelDiffPanel differs={3} active={3} diffs={1000} regressions={15} improvements={80} />);
    expect(container.textContent).toContain("Model Diff");
}); });
