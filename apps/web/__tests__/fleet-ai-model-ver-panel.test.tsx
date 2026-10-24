import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelVerPanel } from "@/components/fleet-ai-model-ver-panel";
describe("FleetAiModelVerPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelVerPanel registries={5} models={200} versions={2000} active={400} />);
    expect(container.textContent).toContain("Model Versioning");
}); });
