import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelVerPanel } from "@/components/fleet-ai-model-ver-panel";
describe("FleetAiModelVerPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelVerPanel versioners={3} active={3} models={200} versions={2000} rollbacks={1} />);
    expect(container.textContent).toContain("Model Versioner");
}); });
