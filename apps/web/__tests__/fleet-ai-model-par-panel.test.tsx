import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelParPanel } from "@/components/fleet-ai-model-par-panel";
describe("FleetAiModelParPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelParPanel configs={5} active={5} gpus={512} tp={8} pp={8} efficiency={92} />);
    expect(container.textContent).toContain("Model Parallelism");
}); });
