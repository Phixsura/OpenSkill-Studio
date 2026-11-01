import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTransformerPanel } from "@/components/fleet-ai-transformer-panel";
describe("FleetAiTransformerPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTransformerPanel engines={4} active={4} models={100} speedup={4} memorySaved={45} />);
    expect(container.textContent).toContain("Transformer Engine");
}); });
