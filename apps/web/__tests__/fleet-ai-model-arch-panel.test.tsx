import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelArchPanel } from "@/components/fleet-ai-model-arch-panel";
describe("FleetAiModelArchPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelArchPanel archives={2} active={2} models={10000} storageTb={5000} retrievals={200} />);
    expect(container.textContent).toContain("Model Archive");
}); });
