import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelWarmPanel } from "@/components/fleet-ai-model-warm-panel";
describe("FleetAiModelWarmPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelWarmPanel managers={4} active={4} warmed={100} prevented={2000000} warmup={10} />);
    expect(container.textContent).toContain("Model Warm-Up");
}); });
