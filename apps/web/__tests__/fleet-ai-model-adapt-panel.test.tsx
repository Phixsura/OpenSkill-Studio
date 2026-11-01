import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelAdaptPanel } from "@/components/fleet-ai-model-adapt-panel";
describe("FleetAiModelAdaptPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelAdaptPanel adapters={3} active={3} providers={10} translations={200000000} />);
    expect(container.textContent).toContain("Model Adapter");
}); });
