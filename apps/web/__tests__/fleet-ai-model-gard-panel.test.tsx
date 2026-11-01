import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelGardPanel } from "@/components/fleet-ai-model-gard-panel";
describe("FleetAiModelGardPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelGardPanel gardens={2} active={2} models={1000} categories={50} downloads={500000} />);
    expect(container.textContent).toContain("Model Garden");
}); });
